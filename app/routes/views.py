from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from app.models import db
from app.models.route import Schedule, Route
from app.models.booking import Booking
from app.routes.auth import login_required, admin_required
from datetime import datetime

views_bp = Blueprint('views', __name__)

@views_bp.route('/')
def index():
    # Fetch distinct sources and destinations to populate search dropdowns
    sources = db.session.query(Route.source).distinct().order_by(Route.source).all()
    destinations = db.session.query(Route.destination).distinct().order_by(Route.destination).all()
    
    source_list = [s[0] for s in sources]
    dest_list = [d[0] for d in destinations]
    
    # Also fetch standard featured routes (can show 3-4 schedules)
    featured_schedules = Schedule.query.filter(Schedule.journey_date >= datetime.today().date()).limit(4).all()
    
    return render_template('index.html', 
                           sources=source_list, 
                           destinations=dest_list, 
                           featured=featured_schedules)


@views_bp.route('/search')
def search():
    source = request.args.get('source', '').strip()
    destination = request.args.get('destination', '').strip()
    date_str = request.args.get('date', '').strip()
    provider = request.args.get('provider', 'all').strip().lower()

    print(f"DEBUG search view request args: source={source!r}, destination={destination!r}, date={date_str!r}, provider={provider!r}")
    
    # Render page first; front-end JS will load results asynchronously from API
    return render_template('search.html', 
                           source=source, 
                           destination=destination, 
                           date=date_str,
                           provider=provider)


@views_bp.route('/booking/<int:schedule_id>')
@login_required
def booking(schedule_id):
    schedule = Schedule.query.get_or_404(schedule_id)
    return render_template('booking.html', schedule=schedule)


@views_bp.route('/ticket/<string:pnr>')
@login_required
def ticket(pnr):
    booking = Booking.query.filter_by(pnr=pnr).first_or_404()
    
    # Verify user owns the booking or is admin
    if booking.user_id != session.get('user_id') and not session.get('is_admin', False):
        flash('Unauthorized access to ticket details.', 'danger')
        return redirect(url_for('views.index'))
        
    return render_template('ticket.html', booking=booking)


@views_bp.route('/profile')
@login_required
def profile():
    return render_template('profile.html')


@views_bp.route('/login')
def login_view():
    # If user is already logged in, redirect to homepage
    if 'user_id' in session:
        return redirect(url_for('views.index'))
    return render_template('login.html')


@views_bp.route('/signup')
def signup_view():
    # If user already logged in, redirect to homepage
    if 'user_id' in session:
        return redirect(url_for('views.index'))
    return render_template('signup.html')


# Admin views
@views_bp.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    return render_template('admin/dashboard.html')


@views_bp.route('/admin/buses')
@admin_required
def admin_buses():
    return render_template('admin/buses.html')


@views_bp.route('/admin/routes')
@admin_required
def admin_routes():
    return render_template('admin/routes.html')


@views_bp.route('/admin/bookings')
@admin_required
def admin_bookings():
    from flask import current_app
    db_uri = current_app.config['SQLALCHEMY_DATABASE_URI']
    bookings = Booking.query.order_by(Booking.booking_date.desc()).all()
    return render_template('admin/bookings.html', bookings=bookings, db_uri=db_uri)
