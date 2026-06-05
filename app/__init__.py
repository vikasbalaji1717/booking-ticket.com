import os
from flask import Flask
from app.config import Config
from app.models import db

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize SQLAlchemy database
    db.init_app(app)
    
    # Import and register Blueprints
    from app.routes.views import views_bp
    from app.routes.auth import auth_bp
    from app.routes.api import api_bp
    from app.routes.admin import admin_bp
    
    app.register_blueprint(views_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    # Context processor to inject variables into templates (like site name, user details)
    @app.context_processor
    def inject_global_vars():
        from flask import session
        from app.models.user import User
        
        user = None
        if 'user_id' in session:
            # Fetch user from database to make sure details are fresh and sync'd
            user = User.query.get(session['user_id'])
            
        return {
            'current_user': user,
            'site_name': 'AeroBus'
        }
    
    # Create tables automatically in development
    with app.app_context():
        # Import models here to register them with SQLAlchemy metadata
        from app.models.user import User
        from app.models.bus import Bus
        from app.models.route import Route, Schedule
        from app.models.booking import Booking, Passenger
        from app.models.payment import Payment
        
        db.create_all()
        print("Database tables initialized successfully.")
        
    return app
