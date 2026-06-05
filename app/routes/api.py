import io
from datetime import datetime
from flask import Blueprint, request, jsonify, session, send_file
from app.models import db
from app.models.user import User
from app.models.bus import Bus
from app.models.route import Route, Schedule
from app.models.booking import Booking, Passenger
from app.models.payment import Payment
from app.routes.auth import login_required
from app.utils.ksrtc_api import fetch_ksrtc_bus_schedules
from fpdf import FPDF

api_bp = Blueprint('api', __name__)

# ----------------- SEARCH & LAYOUTS -----------------

@api_bp.route('/buses/search', methods=['GET'])
def search_buses():
    source = request.args.get('source', '').strip()
    destination = request.args.get('destination', '').strip()
    date_str = request.args.get('date', '').strip()
    
    print(f"DEBUG API search request args: source={source!r}, destination={destination!r}, date={date_str!r}")

    # Optional Filters
    bus_type = request.args.get('type', '').strip()  # AC, Sleeper, Seater, Non-AC
    provider = request.args.get('provider', 'all').strip().lower()
    max_price = request.args.get('max_price', type=float)
    time_filter = request.args.get('time', '').strip()  # morning, afternoon, evening
    
    if not source or not destination or not date_str:
        return jsonify({'success': False, 'message': 'Source, destination, and date are required.'}), 400
        
    try:
        query_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'success': False, 'message': 'Invalid date format. Use YYYY-MM-DD.'}), 400
        
    internal_schedules = []
    internal_query = None
    if provider in ('all', 'internal'):
        # Query schedules matching source, destination and date
        internal_query = Schedule.query.join(Route).join(Bus).filter(
            Route.source == source,
            Route.destination == destination,
            Schedule.journey_date == query_date
        )

        if bus_type:
            bt = bus_type.lower()
            if 'non-ac' in bt:
                internal_query = internal_query.filter(Bus.type.ilike('%Non-AC%'))
            elif 'ac' in bt:
                internal_query = internal_query.filter(Bus.type.ilike('%AC%'))

            if 'sleeper' in bt:
                internal_query = internal_query.filter(Bus.type.ilike('%Sleeper%'))
            elif 'seater' in bt:
                internal_query = internal_query.filter(Bus.type.ilike('%Seater%'))

        print("Source:", source)
        print("Destination:", destination)
        print("Date:", query_date)
        print("Internal Count:", internal_query.count())
        internal_schedules = internal_query.all()

    ksrtc_schedules = []
    if provider in ('all', 'ksrtc'):
        ksrtc_schedules = fetch_ksrtc_bus_schedules(source, destination, query_date)
        print("KSRTC Count:", len(ksrtc_schedules))

        if bus_type:
            bt = bus_type.lower()
            def matches_type(schedule):
                bus_type_value = (schedule.get('bus', {}).get('type') or '').lower()
                if 'non-ac' in bt and 'non-ac' in bus_type_value:
                    return True
                if 'ac' in bt and 'ac' in bus_type_value:
                    return True
                if 'sleeper' in bt and 'sleeper' in bus_type_value:
                    return True
                if 'seater' in bt and 'seater' in bus_type_value:
                    return True
                return False
            ksrtc_schedules = [s for s in ksrtc_schedules if matches_type(s)]

    schedules = []
    if provider in ('all', 'internal'):
        schedules.extend(internal_schedules)
    if provider in ('all', 'ksrtc'):
        schedules.extend(ksrtc_schedules)

    if max_price is not None:
        schedules = [s for s in schedules if float(s['price'] if isinstance(s, dict) else s.price) <= max_price]

    if time_filter:
        filtered_schedules = []
        for s in schedules:
            dep_dt = datetime.fromisoformat(s['departure_time']) if isinstance(s, dict) else s.departure_time
            hour = dep_dt.hour
            if time_filter == 'morning' and hour < 12:
                filtered_schedules.append(s)
            elif time_filter == 'afternoon' and 12 <= hour < 17:
                filtered_schedules.append(s)
            elif time_filter == 'evening' and hour >= 17:
                filtered_schedules.append(s)
        schedules = filtered_schedules

    # Format response
    results = []
    for s in schedules:
        if isinstance(s, dict):
            schedule_data = s.copy()
            schedule_data['available_seats'] = schedule_data.get('available_seats', schedule_data.get('bus', {}).get('capacity', 0))
            schedule_data['provider'] = schedule_data.get('provider', 'KSRTC')
            results.append(schedule_data)
            continue

        # Calculate available seats for internal schedules
        total_seats = s.bus.capacity
        booked_seats_count = Passenger.query.join(Booking).filter(
            Booking.schedule_id == s.id,
            Booking.status == 'Confirmed'
        ).count()
        available_seats = total_seats - booked_seats_count

        schedule_data = s.to_dict()
        schedule_data['available_seats'] = available_seats
        schedule_data['provider'] = 'AeroBus'
        results.append(schedule_data)

    return jsonify({'success': True, 'schedules': results}), 200


@api_bp.route('/buses/<int:schedule_id>', methods=['GET'])
def get_bus_schedule(schedule_id):
    schedule = Schedule.query.get_or_404(schedule_id)
    total_seats = schedule.bus.capacity
    booked_seats = Passenger.query.join(Booking).filter(
        Booking.schedule_id == schedule_id,
        Booking.status == 'Confirmed'
    ).count()
    available_seats = total_seats - booked_seats

    schedule_data = schedule.to_dict()
    schedule_data['available_seats'] = available_seats
    schedule_data['provider'] = 'AeroBus'

    return jsonify({'success': True, 'schedule': schedule_data}), 200


@api_bp.route('/buses/schedules/<int:schedule_id>/seats', methods=['GET'])
@login_required
def get_seats(schedule_id):
    schedule = Schedule.query.get_or_404(schedule_id)
    
    # Query confirmed passengers on this schedule to identify booked seat numbers
    booked_passengers = Passenger.query.join(Booking).filter(
        Booking.schedule_id == schedule_id,
        Booking.status == 'Confirmed'
    ).all()
    
    booked_seats = [p.seat_number for p in booked_passengers]
    
    return jsonify({
        'success': True,
        'capacity': schedule.bus.capacity,
        'bus_type': schedule.bus.type,
        'booked_seats': booked_seats
    }), 200

# ----------------- BOOKINGS & CHECKOUT -----------------

@api_bp.route('/bookings/create', methods=['POST'])
@login_required
def create_booking():
    user_id = session.get('user_id')
    data = request.get_json() or {}
    
    schedule_id = data.get('schedule_id')
    passenger_list = data.get('passengers', [])
    
    if not schedule_id or not passenger_list:
        return jsonify({'success': False, 'message': 'Missing schedule or passenger details.'}), 400
        
    schedule = Schedule.query.get(schedule_id)
    if not schedule:
        return jsonify({'success': False, 'message': 'Schedule not found.'}), 404
        
    # Validate seat selection
    seat_numbers = [p.get('seat_number') for p in passenger_list]
    
    if len(seat_numbers) != len(set(seat_numbers)):
        return jsonify({'success': False, 'message': 'Duplicate seats selected in booking request.'}), 400
        
    for seat in seat_numbers:
        if seat < 1 or seat > schedule.bus.capacity:
            return jsonify({'success': False, 'message': f'Invalid seat number: {seat}.'}), 400
            
    # Check if any seat is already booked (collision check)
    collision = Passenger.query.join(Booking).filter(
        Booking.schedule_id == schedule_id,
        Booking.status == 'Confirmed',
        Passenger.seat_number.in_(seat_numbers)
    ).first()
    
    if collision:
        return jsonify({
            'success': False, 
            'message': f'Seat {collision.seat_number} is already booked. Please select other seats.'
        }), 409
        
    # Transactional save
    try:
        total_amount = len(passenger_list) * schedule.price
        pnr = Booking.generate_pnr()
        
        # Start booking as Pending
        booking = Booking(
            user_id=user_id,
            schedule_id=schedule_id,
            pnr=pnr,
            total_amount=total_amount,
            status='Pending'
        )
        db.session.add(booking)
        db.session.flush()  # Extract booking.id
        
        for p in passenger_list:
            passenger = Passenger(
                booking_id=booking.id,
                name=p.get('name').strip(),
                age=int(p.get('age')),
                gender=p.get('gender'),
                seat_number=int(p.get('seat_number'))
            )
            db.session.add(passenger)
            
        db.session.commit()
        
        # Log pending reservation to terminal
        print(f"\n[RESERVATION LOG] Seat(s) reserved successfully.")
        print(f"  Pending Booking ID: {booking.id}")
        print(f"  Pending PNR: {booking.pnr}")
        print(f"  User ID: {booking.user_id}")
        print(f"  Schedule ID: {booking.schedule_id}")
        print(f"  Seats reserved: {', '.join([str(p.seat_number) for p in booking.passengers])}")
        print("-" * 50 + "\n")
        
        return jsonify({
            'success': True,
            'message': 'Seat reserved. Proceed to payment.',
            'booking_id': booking.id,
            'pnr': booking.pnr,
            'total_amount': total_amount
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Failed to reserve seats: {str(e)}'}), 500


@api_bp.route('/bookings/<int:booking_id>/pay', methods=['POST'])
@login_required
def process_payment(booking_id):
    user_id = session.get('user_id')
    booking = Booking.query.filter_by(id=booking_id, user_id=user_id).first()
    
    if not booking:
        return jsonify({'success': False, 'message': 'Booking record not found.'}), 404
        
    if booking.status == 'Confirmed':
        return jsonify({'success': False, 'message': 'Booking has already been paid and confirmed.'}), 400
        
    data = request.get_json() or {}
    payment_method = data.get('method', 'UPI')
    
    # Check seat conflicts again right before finalizing payment (critical race condition check)
    booked_seats = [p.seat_number for p in booking.passengers]
    conflict = Passenger.query.join(Booking).filter(
        Booking.schedule_id == booking.schedule_id,
        Booking.status == 'Confirmed',
        Passenger.seat_number.in_(booked_seats)
    ).first()
    
    if conflict:
        # If conflict, release pending booking
        booking.status = 'Cancelled'
        db.session.commit()
        return jsonify({
            'success': False,
            'message': f'We are sorry, but Seat {conflict.seat_number} was booked by another user during checkout. Reservation has been cancelled.'
        }), 409
        
    try:
        # Simulating payment confirmation
        booking.status = 'Confirmed'
        
        # Log payment
        txn_id = Payment.generate_transaction_id()
        payment = Payment(
            booking_id=booking.id,
            transaction_id=txn_id,
            method=payment_method,
            amount=booking.total_amount,
            status='Success'
        )
        db.session.add(payment)
        db.session.commit()
        
        # Log confirmed booking to terminal
        seats_str = ", ".join([str(p.seat_number) for p in booking.passengers])
        print(f"\n==================================================")
        print(f"[DATABASE VERIFICATION: NEW BOOKING INSERTED]")
        print(f"  Booking ID   : {booking.id}")
        print(f"  PNR          : {booking.pnr}")
        print(f"  User ID      : {booking.user_id} ({booking.user.username if booking.user else 'N/A'})")
        print(f"  Bus ID       : {booking.schedule.bus_id if booking.schedule else 'N/A'}")
        print(f"  Seat No(s)   : {seats_str}")
        print(f"  Booking Date : {booking.booking_date.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  Total Fare   : Rs. {booking.total_amount:.2f}")
        print(f"  Status       : {booking.status}")
        print(f"==================================================\n")
        
        return jsonify({
            'success': True,
            'message': 'Payment successful! Your ticket is confirmed.',
            'pnr': booking.pnr,
            'transaction_id': txn_id
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Payment simulation failed: {str(e)}'}), 500


@api_bp.route('/bookings/<int:booking_id>/cancel', methods=['POST'])
@login_required
def cancel_booking(booking_id):
    user_id = session.get('user_id')
    booking = Booking.query.filter_by(id=booking_id, user_id=user_id).first()
    
    if not booking:
        return jsonify({'success': False, 'message': 'Booking not found.'}), 404
        
    if booking.status == 'Cancelled':
        return jsonify({'success': False, 'message': 'Ticket has already been cancelled.'}), 400
        
    # Cancellation terms: journey date must be in future (optional but good practice)
    today = datetime.today().date()
    if booking.schedule.journey_date <= today:
        return jsonify({'success': False, 'message': 'Tickets cannot be cancelled on or after the day of journey.'}), 400
        
    try:
        # Update booking status
        booking.status = 'Cancelled'
        
        # Refund payment
        if booking.payment:
            booking.payment.status = 'Refunded'
            
        db.session.commit()
        return jsonify({'success': True, 'message': 'Ticket successfully cancelled. Refund initiated.'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Cancellation failed: {str(e)}'}), 500


@api_bp.route('/bookings/history', methods=['GET'])
@login_required
def booking_history():
    user_id = session.get('user_id')
    bookings = Booking.query.filter_by(user_id=user_id).order_by(Booking.booking_date.desc()).all()
    return jsonify({
        'success': True,
        'bookings': [b.to_dict() for b in bookings]
    }), 200

# ----------------- TICKET PDF GENERATION -----------------

@api_bp.route('/tickets/<string:pnr>/pdf', methods=['GET'])
@login_required
def download_pdf(pnr):
    booking = Booking.query.filter_by(pnr=pnr).first_or_404()
    
    # Check authorization
    if booking.user_id != session.get('user_id') and not session.get('is_admin', False):
        return jsonify({'success': False, 'message': 'Unauthorized access.'}), 403
        
    # Setup PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_margins(15, 15, 15)
    
    # Title & Header
    pdf.set_fill_color(79, 70, 229) # Indigo header bar
    pdf.rect(0, 0, 210, 40, 'F')
    
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 24)
    pdf.cell(0, 15, "AeroBus Ticket Confirmation", align="C", new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font("Helvetica", "I", 10)
    pdf.cell(0, 5, "Fly on Wheels - Safe & Reliable Journeys", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(15)
    
    # Ticket Meta Info
    pdf.set_text_color(15, 23, 42) # Slate
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(90, 8, f"PNR Number: {booking.pnr}", border="B")
    pdf.cell(10)
    pdf.cell(80, 8, f"Status: {booking.status.upper()}", border="B", align="R")
    pdf.ln(12)
    
    # Journey details block
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_fill_color(241, 245, 249) # Light gray block
    pdf.cell(180, 8, "JOURNEY DETAILS", fill=True, new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    
    route_details = f"{booking.schedule.route.source} to {booking.schedule.route.destination}"
    dep_time = booking.schedule.departure_time.strftime('%I:%M %p, %b %d, %Y')
    arr_time = booking.schedule.arrival_time.strftime('%I:%M %p, %b %d, %Y')
    
    pdf.cell(90, 7, f"Route: {route_details}")
    pdf.cell(90, 7, f"Bus: {booking.schedule.bus.name} ({booking.schedule.bus.type})", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(90, 7, f"Departure: {dep_time}")
    pdf.cell(90, 7, f"Arrival: {arr_time}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    
    # Passenger Details table
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_fill_color(241, 245, 249)
    pdf.cell(180, 8, "PASSENGER & SEAT INFORMATION", fill=True, new_x="LMARGIN", new_y="NEXT")
    
    # Table headers
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(80, 7, "Passenger Name", border="B")
    pdf.cell(30, 7, "Age", border="B", align="C")
    pdf.cell(40, 7, "Gender", border="B", align="C")
    pdf.cell(30, 7, "Seat No.", border="B", align="C")
    pdf.ln(8)
    
    pdf.set_font("Helvetica", "", 10)
    for p in booking.passengers:
        pdf.cell(80, 7, p.name)
        pdf.cell(30, 7, str(p.age), align="C")
        pdf.cell(40, 7, p.gender, align="C")
        pdf.cell(30, 7, str(p.seat_number), align="C")
        pdf.ln(7)
    pdf.ln(5)
    
    # Payment Info block
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_fill_color(241, 245, 249)
    pdf.cell(180, 8, "PAYMENT SUMMARY", fill=True, new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font("Helvetica", "", 10)
    txn_id = booking.payment.transaction_id if booking.payment else "N/A"
    pay_method = booking.payment.method if booking.payment else "N/A"
    
    pdf.cell(90, 7, f"Transaction ID: {txn_id}")
    pdf.cell(90, 7, f"Payment Method: {pay_method}", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(90, 7, f"Total Amount Paid: Rs. {booking.total_amount:.2f}")
    pdf.ln(12)
    
    # Terms and Conditions
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(0, 5, "Important Guidelines:", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(100, 116, 139)
    pdf.multi_cell(180, 4, 
                   "1. Please report at the boarding terminal 15 minutes prior to the scheduled departure.\n"
                   "2. Carrying a digital print or copy of this E-Ticket along with a valid ID proof is mandatory during travel.\n"
                   "3. Cancellation requests are eligible for full/partial refund based on the cancellation policy timelines.")
    
    # Output PDF stream
    pdf_output = io.BytesIO()
    pdf_bytes = pdf.output(dest='S')
    pdf_output.write(bytes(pdf_bytes))
    pdf_output.seek(0)
    
    return send_file(
        pdf_output,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f"AeroBus_Ticket_{booking.pnr}.pdf"
    )
