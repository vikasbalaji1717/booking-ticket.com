from app.models import db

class Bus(db.Model):
    __tablename__ = 'buses'
    
    id = db.Column(db.Integer, primary_key=True)
    bus_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # AC Sleeper, AC Seater, Non-AC Sleeper, Non-AC Seater
    capacity = db.Column(db.Integer, nullable=False)  # e.g., 30 seats, 40 seats
    amenities = db.Column(db.String(255), default='')  # WiFi, Charger, Water, Blanket (comma-separated)
    
    # Relationships
    schedules = db.relationship('Schedule', back_populates='bus', lazy=True, cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            'id': self.id,
            'bus_number': self.bus_number,
            'name': self.name,
            'type': self.type,
            'capacity': self.capacity,
            'amenities': [a.strip() for a in self.amenities.split(',')] if self.amenities else []
        }
