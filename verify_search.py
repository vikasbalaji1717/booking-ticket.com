from app import create_app
from app.models import db
from app.models.route import Route, Schedule
from app.models.bus import Bus
from datetime import datetime, date
import pathlib
app = create_app()
app.config.update({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'})
with app.app_context():
    db.drop_all()
    db.create_all()
    b = Bus(bus_number='XX-99-1234', name='Test Bus', type='AC Sleeper', capacity=30, amenities='WiFi')
    r = Route(source='Bangalore', destination='Chennai', distance_km=350.0)
    db.session.add_all([b, r])
    db.session.commit()
    s = Schedule(
        bus_id=b.id,
        route_id=r.id,
        journey_date=date(2026, 6, 6),
        departure_time=datetime.combine(date(2026, 6, 6), datetime.strptime('08:00:00','%H:%M:%S').time()),
        arrival_time=datetime.combine(date(2026, 6, 6), datetime.strptime('14:00:00','%H:%M:%S').time()),
        price=800.0
    )
    db.session.add(s)
    db.session.commit()
    client = app.test_client()
    resp = client.get('/search?source=Bangalore&destination=Chennai&date=2026-06-06')
    print('SEARCH STATUS', resp.status_code)
    html = resp.get_data(as_text=True)
    print('CONTAINS DATA SOURCE', 'data-source="Bangalore"' in html)
    print('CONTAINS DATA DEST', 'data-destination="Chennai"' in html)
    print('CONTAINS DATA DATE', 'data-date="2026-06-06"' in html)
    print('JS FETCH PRESENT', '/api/buses/search' in pathlib.Path('app/static/js/app.js').read_text())
    resp2 = client.get('/api/buses/search?source=Bangalore&destination=Chennai&date=2026-06-06')
    print('API STATUS', resp2.status_code)
    print('API JSON', resp2.get_json())
