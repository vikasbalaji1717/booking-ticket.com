import unittest
import json
from datetime import datetime, date, timedelta
from app import create_app
from app.models import db
from app.models.user import User
from app.models.bus import Bus
from app.models.route import Route, Schedule
from app.models.booking import Booking, Passenger

class AeroBusTestCase(unittest.TestCase):
    def setUp(self):
        """Configure app in testing mode and initialize in-memory database."""
        # Use an in-memory SQLite database for fast isolated testing
        self.app = create_app()
        self.app.config.update({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'WTF_CSRF_ENABLED': False
        })
        self.client = self.app.test_client()
        
        # Enter application context
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Create database tables
        db.create_all()
        self.seed_test_data()

    def tearDown(self):
        """Cleanup database and exit application context."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def seed_test_data(self):
        """Prepopulate in-memory DB with test values."""
        # 1. Seed Volvo Bus
        self.test_bus = Bus(
            bus_number="XX-00-YY-1122", 
            name="Test Volvo", 
            type="AC Sleeper", 
            capacity=30, 
            amenities="WiFi, Charger"
        )
        # 2. Seed Route
        self.test_route = Route(
            source="Delhi", 
            destination="Jaipur", 
            distance_km=270.0
        )
        db.session.add(self.test_bus)
        db.session.add(self.test_route)
        db.session.commit()
        
        # 3. Seed Schedule
        tomorrow = date.today() + timedelta(days=1)
        self.test_schedule = Schedule(
            bus_id=self.test_bus.id,
            route_id=self.test_route.id,
            journey_date=tomorrow,
            departure_time=datetime.combine(tomorrow, datetime.strptime("09:00:00", "%H:%M:%S").time()),
            arrival_time=datetime.combine(tomorrow, datetime.strptime("14:00:00", "%H:%M:%S").time()),
            price=500.0
        )
        db.session.add(self.test_schedule)
        db.session.commit()

    # ----------------- AUTHENTICATION TESTS -----------------
    
    def test_user_registration(self):
        """Test account registration via JSON API."""
        response = self.client.post('/auth/register', 
            data=json.dumps({
                'username': 'Test User',
                'email': 'tester@domain.com',
                'password': 'password123'
            }),
            content_type='application/json'
        )
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(data['success'])
        
        # Double check database has hashing active
        user = User.query.filter_by(email='tester@domain.com').first()
        self.assertIsNotNone(user)
        self.assertNotEqual(user.password_hash, 'password123')
        self.assertTrue(user.check_password('password123'))

    def test_user_login(self):
        """Test user login validation."""
        # Pre-register user
        user = User(username='Login Test', email='logintest@domain.com')
        user.set_password('my_pass_332')
        db.session.add(user)
        db.session.commit()
        
        # Test bad credentials
        response = self.client.post('/auth/login', 
            data=json.dumps({
                'email': 'logintest@domain.com',
                'password': 'wrong_password'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 401)
        
        # Test good credentials
        response = self.client.post('/auth/login', 
            data=json.dumps({
                'email': 'logintest@domain.com',
                'password': 'my_pass_332'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])

    # ----------------- SEARCH TICKETS TESTS -----------------
    
    def test_bus_search(self):
        """Test searching schedules dynamically."""
        tomorrow_str = (date.today() + timedelta(days=1)).strftime('%Y-%m-%d')
        
        # Good search
        response = self.client.get(f'/api/buses/search?source=Delhi&destination=Jaipur&date={tomorrow_str}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(len(data['schedules']), 1)
        self.assertEqual(data['schedules'][0]['price'], 500.0)
        
        # Empty search results (bad route)
        response = self.client.get(f'/api/buses/search?source=Kolkata&destination=Mumbai&date={tomorrow_str}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data['schedules']), 0)

    # ----------------- BOOKING COLLISION TESTS -----------------
    
    def test_seat_booking_collision(self):
        """Test reservation logic and duplicate seating constraints (race-condition check)."""
        # Register a test customer
        user = User(username='Customer', email='customer@domain.com')
        user.set_password('customer123')
        db.session.add(user)
        db.session.commit()
        
        # Login test client
        self.client.post('/auth/login', 
            data=json.dumps({
                'email': 'customer@domain.com',
                'password': 'customer123'
            }),
            content_type='application/json'
        )
        
        # Stage 1: Book seat number 12 (creates Confirmed booking for check)
        booking = Booking(
            user_id=user.id,
            schedule_id=self.test_schedule.id,
            pnr="PNRTEST1",
            total_amount=500.0,
            status="Confirmed"
        )
        db.session.add(booking)
        db.session.flush()
        
        passenger = Passenger(
            booking_id=booking.id,
            name="Alice",
            age=25,
            gender="Female",
            seat_number=12
        )
        db.session.add(passenger)
        db.session.commit()
        
        # Stage 2: Try to book seat number 12 again via POST API
        response = self.client.post('/api/bookings/create',
            data=json.dumps({
                'schedule_id': self.test_schedule.id,
                'passengers': [
                    {'name': 'Bob', 'age': 30, 'gender': 'Male', 'seat_number': 12}
                ]
            }),
            content_type='application/json'
        )
        
        # Should return 409 Conflict status
        self.assertEqual(response.status_code, 409)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertIn("already booked", data['message'])

if __name__ == '__main__':
    unittest.main()
