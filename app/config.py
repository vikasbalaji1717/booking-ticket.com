import os

class Config:
    # Secret Key for session signing
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev_secret_key_change_in_production_129847')
    
    # Base directory of the app
    BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    
    # SQLAlchemy configuration - default to SQLite, easy transition to PostgreSQL/MySQL
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if DATABASE_URL:
        # Compatibility fix for newer SQLAlchemy URI formats (postgres:// -> postgresql://)
        if DATABASE_URL.startswith("postgres://"):
            DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        # Default SQLite database
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'bus_booking.db')}"
        
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session lifetime
    PERMANENT_SESSION_LIFETIME = 86400  # 1 day in seconds
