import uuid
from datetime import datetime
from app.models import db

class Booking(db.Model):
    __tablename__ = 'bookings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    schedule_id = db.Column(db.Integer, db.ForeignKey('schedules.id', ondelete='CASCADE'), nullable=False)
    pnr = db.Column(db.String(20), unique=True, nullable=False, index=True)
    booking_date = db.Column(db.DateTime, default=datetime.utcnow)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='Confirmed')  # Confirmed, Cancelled
    
    # Relationships
    user = db.relationship('User', back_populates='bookings')
    schedule = db.relationship('Schedule', back_populates='bookings')
    passengers = db.relationship('Passenger', back_populates='booking', lazy=True, cascade="all, delete-orphan")
    payment = db.relationship('Payment', back_populates='booking', uselist=False, cascade="all, delete-orphan")
    
    @staticmethod
    def generate_pnr():
        """Generates a unique 8-character uppercase alphanumeric PNR."""
        return "PNR" + str(uuid.uuid4().hex[:7].upper())
        
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'schedule_id': self.schedule_id,
            'pnr': self.pnr,
            'booking_date': self.booking_date.isoformat(),
            'total_amount': self.total_amount,
            'status': self.status,
            'passengers': [p.to_dict() for p in self.passengers],
            'payment': self.payment.to_dict() if self.payment else None,
            'schedule': self.schedule.to_dict() if self.schedule else None
        }


class Passenger(db.Model):
    __tablename__ = 'passengers'
    
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)  # Male, Female, Other
    seat_number = db.Column(db.Integer, nullable=False)
    
    # Relationships
    booking = db.relationship('Booking', back_populates='passengers')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'age': self.age,
            'gender': self.gender,
            'seat_number': self.seat_number
        }
