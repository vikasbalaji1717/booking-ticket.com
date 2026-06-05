import uuid
from datetime import datetime
from app.models import db

class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id', ondelete='CASCADE'), nullable=False)
    transaction_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    method = db.Column(db.String(50), nullable=False)  # Card, UPI, NetBanking, Wallet
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='Success')  # Success, Failed, Refunded
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    booking = db.relationship('Booking', back_populates='payment')
    
    @staticmethod
    def generate_transaction_id():
        """Generates a unique transaction identifier."""
        return "TXN" + str(uuid.uuid4().hex[:12].upper())
        
    def to_dict(self):
        return {
            'id': self.id,
            'booking_id': self.booking_id,
            'transaction_id': self.transaction_id,
            'method': self.method,
            'amount': self.amount,
            'status': self.status,
            'payment_date': self.payment_date.isoformat()
        }
