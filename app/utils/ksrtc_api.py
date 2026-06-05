import os
import json
import urllib.request
import urllib.error
from datetime import datetime, timedelta


def fetch_ksrtc_bus_schedules(source, destination, journey_date):
    """Fetch KSRTC-style bus schedule data.

    If KSRTC API settings are configured, attempt a live request.
    Otherwise return a local KSRTC-style stub response.
    """
    api_url = os.environ.get('KSRTC_API_URL')
    if api_url:
        try:
            url = f"{api_url}?source={urllib.request.quote(source)}&destination={urllib.request.quote(destination)}&date={journey_date.isoformat()}"
            with urllib.request.urlopen(url, timeout=10) as resp:
                payload = resp.read().decode('utf-8')
                data = json.loads(payload)
                if isinstance(data, dict) and data.get('schedules'):
                    return data['schedules']
        except (urllib.error.URLError, json.JSONDecodeError, ValueError):
            pass

    # Fallback stubbed KSRTC schedule data for supported routes.
    known_routes = {
        ('Bangalore', 'Chennai'): [
            {
                'id': 1001,
                'route': {'source': 'Bangalore', 'destination': 'Chennai', 'distance_km': 355.0},
                'bus': {
                    'id': 201,
                    'bus_number': 'KA-01-BS-1001',
                    'name': 'KSRTC AC Sleeper',
                    'type': 'AC Sleeper',
                    'capacity': 30,
                    'amenities': ['WiFi', 'AC', 'Blanket', 'Charging Port'],
                    'operator': 'KSRTC'
                },
                'departure_time': datetime.combine(journey_date, datetime.strptime('22:30', '%H:%M').time()).isoformat(),
                'arrival_time': (datetime.combine(journey_date, datetime.strptime('22:30', '%H:%M').time()) + timedelta(hours=7, minutes=15)).isoformat(),
                'journey_date': journey_date.isoformat(),
                'price': 1250.0,
                'provider': 'KSRTC'
            },
            {
                'id': 1002,
                'route': {'source': 'Bangalore', 'destination': 'Chennai', 'distance_km': 355.0},
                'bus': {
                    'id': 202,
                    'bus_number': 'KA-01-BS-1002',
                    'name': 'KSRTC Volvo Seater',
                    'type': 'AC Seater',
                    'capacity': 45,
                    'amenities': ['WiFi', 'AC', 'Recliner Seat'],
                    'operator': 'KSRTC'
                },
                'departure_time': datetime.combine(journey_date, datetime.strptime('06:00', '%H:%M').time()).isoformat(),
                'arrival_time': (datetime.combine(journey_date, datetime.strptime('06:00', '%H:%M').time()) + timedelta(hours=6, minutes=30)).isoformat(),
                'journey_date': journey_date.isoformat(),
                'price': 980.0,
                'provider': 'KSRTC'
            }
        ],
        ('Delhi', 'Jaipur'): [
            {
                'id': 1003,
                'route': {'source': 'Delhi', 'destination': 'Jaipur', 'distance_km': 270.0},
                'bus': {
                    'id': 203,
                    'bus_number': 'DL-01-KS-203',
                    'name': 'KSRTC Express',
                    'type': 'AC Seater',
                    'capacity': 40,
                    'amenities': ['AC', 'WiFi', 'Water Bottle'],
                    'operator': 'KSRTC'
                },
                'departure_time': datetime.combine(journey_date, datetime.strptime('08:00', '%H:%M').time()).isoformat(),
                'arrival_time': (datetime.combine(journey_date, datetime.strptime('08:00', '%H:%M').time()) + timedelta(hours=5, minutes=0)).isoformat(),
                'journey_date': journey_date.isoformat(),
                'price': 650.0,
                'provider': 'KSRTC'
            }
        ]
    }

    return known_routes.get((source, destination), [])
