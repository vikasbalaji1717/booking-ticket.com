import os
from datetime import datetime, date, timedelta
from app import create_app
from app.models import db
from app.models.user import User
from app.models.bus import Bus
from app.models.route import Route, Schedule
from app.models.booking import Booking, Passenger
from app.models.payment import Payment

def seed_database():
    app = create_app()
    with app.app_context():
        print("Clearing existing database tables...")
        db.drop_all()
        db.create_all()
        
        print("Seeding Users...")
        # Seed Administrator
        admin = User(username="Admin Manager", email="admin@aerobus.com", is_admin=True)
        admin.set_password("admin123")
        db.session.add(admin)
        
        # Seed Customer
        customer = User(username="Vikas Kumar", email="user@aerobus.com", is_admin=False)
        customer.set_password("user123")
        db.session.add(customer)
        
        db.session.commit()
        
        print("Seeding Buses...")
        buses = [
            Bus(bus_number="DL-01-A-8899", name="AeroBus Volvo Multi-Axle", type="AC Sleeper", capacity=30, amenities="WiFi, Charger, Water, Blanket, Pillow"),
            Bus(bus_number="MH-12-PQ-4530", name="AeroBus Scania Touring", type="AC Seater", capacity=40, amenities="WiFi, Charger, Water"),
            Bus(bus_number="KA-03-M-1122", name="National Express (Tata)", type="Non-AC Seater", capacity=40, amenities="Water"),
            Bus(bus_number="DL-02-B-5566", name="Royal Travels (Ashok Leyland)", type="Non-AC Sleeper", capacity=32, amenities="Blanket, Pillow"),
            Bus(bus_number="KA-19-AB-3001", name="GreenLine Volvo Super Deluxe", type="AC Sleeper", capacity=32, amenities="WiFi, Charger, Water, Snack"),
            Bus(bus_number="KA-22-BC-4021", name="SilkRoute Mercedes", type="AC Seater", capacity=44, amenities="WiFi, Recliner Seats, Charger"),
            Bus(bus_number="TN-07-DE-5623", name="Tamil Nadu Express", type="Non-AC Seater", capacity=42, amenities="Water"),
            Bus(bus_number="KL-07-FG-7812", name="Kerala Lotus", type="AC Sleeper", capacity=30, amenities="WiFi, Charger, Blanket, Pillow")
        ]
        for b in buses:
            db.session.add(b)
        db.session.commit()
        
        print("Seeding Routes...")
        routes = [
            Route(source="Bangalore", destination="Pune", distance_km=840.0),
            Route(source="Delhi", destination="Jaipur", distance_km=270.0),
            Route(source="Mumbai", destination="Pune", distance_km=150.0),
            Route(source="Bangalore", destination="Chennai", distance_km=350.0),
            Route(source="Delhi", destination="Chandigarh", distance_km=240.0),
            Route(source="Bangalore", destination="Mysore", distance_km=145.0),
            Route(source="Bangalore", destination="Mangalore", distance_km=355.0),
            Route(source="Mysore", destination="Hubli", distance_km=260.0),
            Route(source="Chennai", destination="Coimbatore", distance_km=500.0),
            Route(source="Kochi", destination="Trivandrum", distance_km=200.0),
            Route(source="Hyderabad", destination="Vijayawada", distance_km=275.0),
            Route(source="Bangalore", destination="Hubli", distance_km=415.0),
            Route(source="Mysore", destination="Mangalore", distance_km=360.0)
        ]
        for r in routes:
            db.session.add(r)
        db.session.commit()
        
        # Pull references
        route_del_jai = Route.query.filter_by(source="Delhi", destination="Jaipur").first()
        route_mum_pun = Route.query.filter_by(source="Mumbai", destination="Pune").first()
        route_blr_chn = Route.query.filter_by(source="Bangalore", destination="Chennai").first()
        route_blr_mys = Route.query.filter_by(source="Bangalore", destination="Mysore").first()
        route_blr_man = Route.query.filter_by(source="Bangalore", destination="Mangalore").first()
        route_mys_hub = Route.query.filter_by(source="Mysore", destination="Hubli").first()
        route_chn_cov = Route.query.filter_by(source="Chennai", destination="Coimbatore").first()
        route_kci_trv = Route.query.filter_by(source="Kochi", destination="Trivandrum").first()
        route_hyd_vja = Route.query.filter_by(source="Hyderabad", destination="Vijayawada").first()
        route_blr_hub = Route.query.filter_by(source="Bangalore", destination="Hubli").first()
        route_mys_man = Route.query.filter_by(source="Mysore", destination="Mangalore").first()
        
        bus_volvo = Bus.query.filter_by(bus_number="DL-01-A-8899").first()
        bus_scania = Bus.query.filter_by(bus_number="MH-12-PQ-4530").first()
        bus_tata = Bus.query.filter_by(bus_number="KA-03-M-1122").first()
        bus_green = Bus.query.filter_by(bus_number="KA-19-AB-3001").first()
        bus_silk = Bus.query.filter_by(bus_number="KA-22-BC-4021").first()
        bus_tn = Bus.query.filter_by(bus_number="TN-07-DE-5623").first()
        bus_kl = Bus.query.filter_by(bus_number="KL-07-FG-7812").first()
        
        print("Seeding Schedules...")
        today = date.today()
        tomorrow = today + timedelta(days=1)
        day_after = today + timedelta(days=2)
        
        schedules = [
            # Delhi to Jaipur - Tomorrow Morning
            Schedule(
                bus_id=bus_volvo.id,
                route_id=route_del_jai.id,
                journey_date=tomorrow,
                departure_time=datetime.combine(tomorrow, datetime.strptime("08:00:00", "%H:%M:%S").time()),
                arrival_time=datetime.combine(tomorrow, datetime.strptime("13:00:00", "%H:%M:%S").time()),
                price=650.0
            ),
            # Delhi to Jaipur - Tomorrow Evening
            Schedule(
                bus_id=bus_scania.id,
                route_id=route_del_jai.id,
                journey_date=tomorrow,
                departure_time=datetime.combine(tomorrow, datetime.strptime("16:00:00", "%H:%M:%S").time()),
                arrival_time=datetime.combine(tomorrow, datetime.strptime("21:00:00", "%H:%M:%S").time()),
                price=550.0
            ),
            # Mumbai to Pune - Tomorrow Afternoon
            Schedule(
                bus_id=bus_tata.id,
                route_id=route_mum_pun.id,
                journey_date=tomorrow,
                departure_time=datetime.combine(tomorrow, datetime.strptime("12:00:00", "%H:%M:%S").time()),
                arrival_time=datetime.combine(tomorrow, datetime.strptime("15:30:00", "%H:%M:%S").time()),
                price=250.0
            ),
            # Bangalore to Chennai - Day After Tomorrow Overnight
            Schedule(
                bus_id=bus_volvo.id,
                route_id=route_blr_chn.id,
                journey_date=day_after,
                departure_time=datetime.combine(day_after, datetime.strptime("22:00:00", "%H:%M:%S").time()),
                arrival_time=datetime.combine(day_after + timedelta(days=1), datetime.strptime("05:30:00", "%H:%M:%S").time()),
                price=890.0
            ),
            # Bangalore to Mysore - Tomorrow Midday
            Schedule(
                bus_id=bus_scania.id,
                route_id=route_blr_mys.id,
                journey_date=tomorrow,
                departure_time=datetime.combine(tomorrow, datetime.strptime("10:00:00", "%H:%M:%S").time()),
                arrival_time=datetime.combine(tomorrow, datetime.strptime("13:00:00", "%H:%M:%S").time()),
                price=350.0
            ),
            # Bangalore to Mangalore - Day After Tomorrow Morning
            Schedule(
                bus_id=bus_tata.id,
                route_id=route_blr_man.id,
                journey_date=day_after,
                departure_time=datetime.combine(day_after, datetime.strptime("07:00:00", "%H:%M:%S").time()),
                arrival_time=datetime.combine(day_after, datetime.strptime("14:00:00", "%H:%M:%S").time()),
                price=750.0
            ),
            # Mysore to Hubli - Day After Tomorrow Afternoon
            Schedule(
                bus_id=bus_volvo.id,
                route_id=route_mys_hub.id,
                journey_date=day_after,
                departure_time=datetime.combine(day_after, datetime.strptime("13:30:00", "%H:%M:%S").time()),
                arrival_time=datetime.combine(day_after, datetime.strptime("19:30:00", "%H:%M:%S").time()),
                price=620.0
            ),
            # Chennai to Coimbatore - Tomorrow Night
            Schedule(
                bus_id=bus_kl.id,
                route_id=route_chn_cov.id,
                journey_date=tomorrow,
                departure_time=datetime.combine(tomorrow, datetime.strptime("21:00:00", "%H:%M:%S").time()),
                arrival_time=datetime.combine(tomorrow + timedelta(days=1), datetime.strptime("03:00:00", "%H:%M:%S").time()),
                price=780.0
            ),
            # Kochi to Trivandrum - Tomorrow Evening
            Schedule(
                bus_id=bus_tn.id,
                route_id=route_kci_trv.id,
                journey_date=tomorrow,
                departure_time=datetime.combine(tomorrow, datetime.strptime("17:30:00", "%H:%M:%S").time()),
                arrival_time=datetime.combine(tomorrow, datetime.strptime("20:30:00", "%H:%M:%S").time()),
                price=320.0
            ),
            # Bangalore to Hubli - Day After Tomorrow Afternoon
            Schedule(
                bus_id=bus_green.id,
                route_id=route_blr_hub.id,
                journey_date=day_after,
                departure_time=datetime.combine(day_after, datetime.strptime("14:00:00", "%H:%M:%S").time()),
                arrival_time=datetime.combine(day_after, datetime.strptime("20:30:00", "%H:%M:%S").time()),
                price=720.0
            ),
            # Mysore to Mangalore - Tomorrow Morning
            Schedule(
                bus_id=bus_silk.id,
                route_id=route_mys_man.id,
                journey_date=tomorrow,
                departure_time=datetime.combine(tomorrow, datetime.strptime("09:00:00", "%H:%M:%S").time()),
                arrival_time=datetime.combine(tomorrow, datetime.strptime("14:00:00", "%H:%M:%S").time()),
                price=420.0
            )
        ]
        for s in schedules:
            db.session.add(s)
        db.session.commit()
        
        # Fetch customer and a schedule to seed completed bookings
        cust_user = User.query.filter_by(email="user@aerobus.com").first()
        active_sched = Schedule.query.first()
        
        print("Seeding Sample Completed Bookings...")
        # Create confirmed booking
        pnr_code = Booking.generate_pnr()
        booking = Booking(
            user_id=cust_user.id,
            schedule_id=active_sched.id,
            pnr=pnr_code,
            total_amount=1300.0,  # 2 seats * 650.0
            status="Confirmed"
        )
        db.session.add(booking)
        db.session.flush() # Get booking ID
        
        # Add Passengers
        p1 = Passenger(booking_id=booking.id, name="Vikas Kumar", age=28, gender="Male", seat_number=7)
        p2 = Passenger(booking_id=booking.id, name="Suresh Kumar", age=54, gender="Male", seat_number=8)
        db.session.add(p1)
        db.session.add(p2)
        
        # Add Payment log
        txn_id = Payment.generate_transaction_id()
        payment = Payment(
            booking_id=booking.id,
            transaction_id=txn_id,
            method="UPI",
            amount=1300.0,
            status="Success"
        )
        db.session.add(payment)
        
        db.session.commit()
        print("Database seeded successfully with test records!")

if __name__ == '__main__':
    seed_database()
