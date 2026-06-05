from functools import wraps
from flask import Blueprint, request, jsonify, session, redirect, url_for, flash
from app.models import db
from app.models.user import User

auth_bp = Blueprint('auth', __name__)

# Authentication Decorators
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            if request.path.startswith('/api/'):
                return jsonify({'success': False, 'message': 'Unauthorized. Please log in.'}), 401
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login_page'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or not session.get('is_admin', False):
            if request.path.startswith('/api/'):
                return jsonify({'success': False, 'message': 'Forbidden. Admin access required.'}), 403
            flash('Admin access is required to view that page.', 'danger')
            return redirect(url_for('views.index'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@auth_bp.route('/register', methods=['POST'])
def register():
    # Accept JSON (AJAX) or form-encoded submissions
    if request.is_json:
        data = request.get_json() or {}
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        is_admin = bool(data.get('is_admin', False))
    else:
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        is_admin = bool(request.form.get('is_admin'))
    
    if not username or not email or not password:
        if request.is_json:
            return jsonify({'success': False, 'message': 'Please fill all required fields.'}), 400
        flash('Please fill all required fields.', 'warning')
        return redirect(url_for('views.signup_view'))
        
    if User.query.filter_by(email=email).first():
        if request.is_json:
            return jsonify({'success': False, 'message': 'Email address is already registered.'}), 400
        flash('Email address is already registered.', 'danger')
        return redirect(url_for('views.signup_view'))
        
    try:
        new_user = User(username=username, email=email, is_admin=is_admin)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        
        # Log the user in automatically after registration
        session.clear()
        session['user_id'] = new_user.id
        session['username'] = new_user.username
        session['email'] = new_user.email
        session['is_admin'] = new_user.is_admin
        session.permanent = True

        if request.is_json:
            return jsonify({
                'success': True,
                'message': 'Account registered successfully!',
                'user': new_user.to_dict()
            }), 201
        flash('Account registered successfully!', 'success')
        return redirect(url_for('views.index'))
    except Exception as e:
        db.session.rollback()
        if request.is_json:
            return jsonify({'success': False, 'message': f'Server error: {str(e)}'}), 500
        flash(f'Server error: {str(e)}', 'danger')
        return redirect(url_for('views.signup_view'))


@auth_bp.route('/login', methods=['POST'])
def login():
    # Support JSON (AJAX) and form-encoded submissions
    if request.is_json:
        data = request.get_json() or {}
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
    else:
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

    if not email or not password:
        if request.is_json:
            return jsonify({'success': False, 'message': 'Please enter your email and password.'}), 400
        flash('Please enter your email and password.', 'warning')
        return redirect(url_for('views.login_view'))

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        if request.is_json:
            return jsonify({'success': False, 'message': 'Invalid email or password.'}), 401
        flash('Invalid email or password.', 'danger')
        return redirect(url_for('views.login_view'))

    # Set up session variables
    session.clear()
    session['user_id'] = user.id
    session['username'] = user.username
    session['email'] = user.email
    session['is_admin'] = user.is_admin
    session.permanent = True

    if request.is_json:
        return jsonify({
            'success': True,
            'message': f'Welcome back, {user.username}!',
            'user': user.to_dict()
        }), 200
    flash(f'Welcome back, {user.username}!', 'success')
    return redirect(url_for('views.index'))


@auth_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    if request.headers.get('Accept') == 'application/json' or request.path.startswith('/api/'):
        return jsonify({'success': True, 'message': 'Logged out successfully.'})
    flash('You have been logged out.', 'info')
    return redirect(url_for('views.index'))


@auth_bp.route('/login_page', methods=['GET'])
def login_page():
    # Helper redirection view for base template/login-required redirections
    return redirect(url_for('views.login_view'))
