from datetime import datetime
from app.models import db

class Route(db.Model):
    __tablename__ = 'routes'
    
    id = db.Column(db.Integer, primary_key=True)
    source = db.Column(db.String(100), nullable=False, index=True)
    destination = db.Column(db.String(100), nullable=False, index=True)
    distance_km = db.Column(db.Float, nullable=False)
    
    # Relationships
    schedules = db.relationship('Schedule', back_populates='route', lazy=True, cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            'id': self.id,
            'source': self.source,
            'destination': self.destination,
            'distance_km': self.distance_km
        }


class Schedule(db.Model):
    __tablename__ = 'schedules'
    
    id = db.Column(db.Integer, primary_key=True)
    bus_id = db.Column(db.Integer, db.ForeignKey('buses.id', ondelete='CASCADE'), nullable=False)
    route_id = db.Column(db.Integer, db.ForeignKey('routes.id', ondelete='CASCADE'), nullable=False)
    departure_time = db.Column(db.DateTime, nullable=False)
    arrival_time = db.Column(db.DateTime, nullable=False)
    journey_date = db.Column(db.Date, nullable=False, index=True)
    price = db.Column(db.Float, nullable=False)
    
    # Relationships
    bus = db.relationship('Bus', back_populates='schedules')
    route = db.relationship('Route', back_populates='schedules')
    bookings = db.relationship('Booking', back_populates='schedule', lazy=True, cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            'id': self.id,
            'bus': self.bus.to_dict() if self.bus else None,
            'route': self.route.to_dict() if self.route else None,
            'departure_time': self.departure_time.isoformat(),
            'arrival_time': self.arrival_time.isoformat(),
            'journey_date': self.journey_date.isoformat(),
            'price': self.price
        }
