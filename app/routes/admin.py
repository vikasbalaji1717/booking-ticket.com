from datetime import datetime
from flask import Blueprint, request, jsonify, session
from app.models import db
from app.models.user import User
from app.models.bus import Bus
from app.models.route import Route, Schedule
from app.models.booking import Booking, Passenger
from app.models.payment import Payment
from app.routes.auth import admin_required

admin_bp = Blueprint('admin_api', __name__)

# Apply admin restriction to all endpoints in this blueprint

@admin_bp.route('/stats', methods=['GET'])
@admin_required
def get_stats():
    # 1. Total Revenue
    revenue_row = db.session.query(db.func.sum(Booking.total_amount)).filter(Booking.status == 'Confirmed').first()
    total_revenue = revenue_row[0] if revenue_row[0] is not None else 0.0
    
    # 2. Total Bookings
    total_bookings = Booking.query.filter_by(status='Confirmed').count()
    
    # 3. Total Buses
    total_buses = Bus.query.count()
    
    # 4. Active Schedules
    active_schedules = Schedule.query.filter(Schedule.journey_date >= datetime.today().date()).count()
    
    # 5. Recent Bookings (last 5)
    recent_bookings = Booking.query.order_by(Booking.booking_date.desc()).limit(5).all()
    recent_list = []
    for b in recent_bookings:
        recent_list.append({
            'pnr': b.pnr,
            'user': b.user.username if b.user else 'Unknown',
            'route': f"{b.schedule.route.source} -> {b.schedule.route.destination}" if b.schedule and b.schedule.route else 'Unknown',
            'amount': b.total_amount,
            'status': b.status,
            'date': b.booking_date.strftime('%Y-%m-%d %H:%M')
        })
        
    return jsonify({
        'success': True,
        'stats': {
            'total_revenue': total_revenue,
            'total_bookings': total_bookings,
            'total_buses': total_buses,
            'active_schedules': active_schedules,
            'recent_bookings': recent_list
        }
    }), 200

# ----------------- BUS CRUD -----------------

@admin_bp.route('/buses', methods=['GET', 'POST'])
@admin_required
def manage_buses():
    if request.method == 'GET':
        buses = Bus.query.all()
        return jsonify({'success': True, 'buses': [b.to_dict() for b in buses]}), 200
        
    elif request.method == 'POST':
        data = request.get_json() or {}
        bus_id = data.get('id')  # If present, we update
        
        bus_number = data.get('bus_number', '').strip().upper()
        name = data.get('name', '').strip()
        bus_type = data.get('type', '').strip()
        capacity = data.get('capacity', type=int)
        amenities = data.get('amenities', '').strip()
        
        if not bus_number or not name or not bus_type or not capacity:
            return jsonify({'success': False, 'message': 'All fields are required.'}), 400
            
        try:
            if bus_id:
                # Update
                bus = Bus.query.get(bus_id)
                if not bus:
                    return jsonify({'success': False, 'message': 'Bus not found.'}), 404
                # Check bus number uniqueness if changed
                if bus.bus_number != bus_number and Bus.query.filter_by(bus_number=bus_number).first():
                    return jsonify({'success': False, 'message': f'Bus number {bus_number} is already in use.'}), 400
                
                bus.bus_number = bus_number
                bus.name = name
                bus.type = bus_type
                bus.capacity = capacity
                bus.amenities = amenities
                message = "Bus details updated successfully!"
            else:
                # Create
                if Bus.query.filter_by(bus_number=bus_number).first():
                    return jsonify({'success': False, 'message': f'Bus number {bus_number} is already in use.'}), 400
                    
                bus = Bus(bus_number=bus_number, name=name, type=bus_type, capacity=capacity, amenities=amenities)
                db.session.add(bus)
                message = "Bus added successfully!"
                
            db.session.commit()
            return jsonify({'success': True, 'message': message, 'bus': bus.to_dict()}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': f'Failed to save bus: {str(e)}'}), 500


@admin_bp.route('/buses/<int:bus_id>/delete', methods=['POST', 'DELETE'])
@admin_required
def delete_bus(bus_id):
    bus = Bus.query.get_or_404(bus_id)
    try:
        db.session.delete(bus)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Bus and all associated schedules deleted.'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Failed to delete bus: {str(e)}'}), 500

# ----------------- ROUTE & SCHEDULE CRUD -----------------

@admin_bp.route('/routes', methods=['GET', 'POST'])
@admin_required
def manage_routes():
    if request.method == 'GET':
        routes = Route.query.all()
        # Join routes with their schedules for a complete picture
        route_list = []
        for r in routes:
            d = r.to_dict()
            d['schedules_count'] = len(r.schedules)
            route_list.append(d)
        return jsonify({'success': True, 'routes': route_list}), 200
        
    elif request.method == 'POST':
        data = request.get_json() or {}
        route_id = data.get('id')
        
        source = data.get('source', '').strip()
        destination = data.get('destination', '').strip()
        distance = data.get('distance_km', type=float)
        
        if not source or not destination or distance is None:
            return jsonify({'success': False, 'message': 'Source, destination, and distance are required.'}), 400
            
        try:
            if route_id:
                route = Route.query.get(route_id)
                if not route:
                    return jsonify({'success': False, 'message': 'Route not found.'}), 404
                route.source = source
                route.destination = destination
                route.distance_km = distance
                message = "Route details updated successfully!"
            else:
                route = Route(source=source, destination=destination, distance_km=distance)
                db.session.add(route)
                message = "Route added successfully!"
                
            db.session.commit()
            return jsonify({'success': True, 'message': message, 'route': route.to_dict()}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': f'Failed to save route: {str(e)}'}), 500


@admin_bp.route('/routes/<int:route_id>/delete', methods=['POST', 'DELETE'])
@admin_required
def delete_route(route_id):
    route = Route.query.get_or_404(route_id)
    try:
        db.session.delete(route)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Route and all associated schedules deleted.'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Failed to delete route: {str(e)}'}), 500


@admin_bp.route('/schedules', methods=['GET', 'POST'])
@admin_required
def manage_schedules():
    if request.method == 'GET':
        schedules = Schedule.query.all()
        return jsonify({'success': True, 'schedules': [s.to_dict() for s in schedules]}), 200
        
    elif request.method == 'POST':
        data = request.get_json() or {}
        sched_id = data.get('id')
        
        bus_id = data.get('bus_id', type=int)
        route_id = data.get('route_id', type=int)
        price = data.get('price', type=float)
        dep_str = data.get('departure_time', '').strip()  # Format YYYY-MM-DDTHH:MM
        arr_str = data.get('arrival_time', '').strip()    # Format YYYY-MM-DDTHH:MM
        date_str = data.get('journey_date', '').strip()   # Format YYYY-MM-DD
        
        if not bus_id or not route_id or not price or not dep_str or not arr_str or not date_str:
            return jsonify({'success': False, 'message': 'All fields are required.'}), 400
            
        try:
            dep_time = datetime.strptime(dep_str, '%Y-%m-%dT%H:%M')
            arr_time = datetime.strptime(arr_str, '%Y-%m-%dT%H:%M')
            journey_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            
            if arr_time <= dep_time:
                return jsonify({'success': False, 'message': 'Arrival time must be after departure time.'}), 400
                
            if sched_id:
                schedule = Schedule.query.get(sched_id)
                if not schedule:
                    return jsonify({'success': False, 'message': 'Schedule not found.'}), 404
                schedule.bus_id = bus_id
                schedule.route_id = route_id
                schedule.price = price
                schedule.departure_time = dep_time
                schedule.arrival_time = arr_time
                schedule.journey_date = journey_date
                message = "Schedule updated successfully!"
            else:
                schedule = Schedule(
                    bus_id=bus_id, route_id=route_id, price=price,
                    departure_time=dep_time, arrival_time=arr_time, journey_date=journey_date
                )
                db.session.add(schedule)
                message = "Schedule created successfully!"
                
            db.session.commit()
            return jsonify({'success': True, 'message': message, 'schedule': schedule.to_dict()}), 200
        except ValueError:
            return jsonify({'success': False, 'message': 'Incorrect date or time formats.'}), 400
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': f'Failed to save schedule: {str(e)}'}), 500


@admin_bp.route('/schedules/<int:schedule_id>/delete', methods=['POST', 'DELETE'])
@admin_required
def delete_schedule(schedule_id):
    sched = Schedule.query.get_or_404(schedule_id)
    try:
        db.session.delete(sched)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Schedule and all related bookings deleted.'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Failed to delete schedule: {str(e)}'}), 500

# ----------------- BOOKING VIEWER & OVERRIDE -----------------

@admin_bp.route('/bookings_list', methods=['GET'])
@admin_required
def get_all_bookings():
    bookings = Booking.query.order_by(Booking.booking_date.desc()).all()
    return jsonify({
        'success': True,
        'bookings': [b.to_dict() for b in bookings]
    }), 200


@admin_bp.route('/bookings/<int:booking_id>/cancel', methods=['POST'])
@admin_required
def admin_cancel_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    
    if booking.status == 'Cancelled':
        return jsonify({'success': False, 'message': 'This booking is already cancelled.'}), 400
        
    try:
        booking.status = 'Cancelled'
        if booking.payment:
            booking.payment.status = 'Refunded'
        db.session.commit()
        return jsonify({'success': True, 'message': 'Booking successfully cancelled by Administrator.'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Admin cancellation failed: {str(e)}'}), 500
