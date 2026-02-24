from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, unset_jwt_cookies, set_access_cookies
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

from config import Config
from models import db, User, Appointment, Prescription, Medicine, Notification
from auth import get_current_user
from datetime import datetime, date
import os

# Import blueprints
from routes.admin import admin_bp
from routes.doctor import doctor_bp
from routes.patient import patient_bp
from routes.receptionist import receptionist_bp
from routes.pharmacist import pharmacist_bp

# Import services
from services.chatbot_service import process_chatbot_message

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
jwt = JWTManager(app)

# Register blueprints
app.register_blueprint(admin_bp)
app.register_blueprint(doctor_bp)
app.register_blueprint(patient_bp)
app.register_blueprint(receptionist_bp)
app.register_blueprint(pharmacist_bp)

# Create database tables
with app.app_context():
    db.create_all()
    
    # Create default admin user if doesn't exist
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@hospital.com',
            role='admin',
            is_active=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        
        # Create sample users for testing
        doctor = User(username='doctor1', email='doctor@hospital.com', role='doctor', is_active=True)
        doctor.set_password('doctor123')
        db.session.add(doctor)
        
        patient = User(username='patient1', email='patient@hospital.com', role='patient', is_active=True)
        patient.set_password('patient123')
        db.session.add(patient)
        
        receptionist = User(username='receptionist1', email='receptionist@hospital.com', role='receptionist', is_active=True)
        receptionist.set_password('receptionist123')
        db.session.add(receptionist)
        
        pharmacist = User(username='pharmacist1', email='pharmacist@hospital.com', role='pharmacist', is_active=True)
        pharmacist.set_password('pharmacist123')
        db.session.add(pharmacist)
        
        # Add sample medicines
        medicines = [
            Medicine(name='Paracetamol 500mg', quantity=500, expiry_date=date(2026, 12, 31)),
            Medicine(name='Ibuprofen 400mg', quantity=300, expiry_date=date(2026, 11, 30)),
            Medicine(name='Amoxicillin 250mg', quantity=45, expiry_date=date(2026, 6, 30)),
            Medicine(name='Omeprazole 20mg', quantity=200, expiry_date=date(2026, 10, 15)),
            Medicine(name='Aspirin 75mg', quantity=30, expiry_date=date(2026, 3, 15)),
        ]
        
        for medicine in medicines:
            db.session.add(medicine)
        
        db.session.commit()
        print("Database initialized with default users and sample data!")
        print("Admin: admin / admin123")
        print("Doctor: doctor1 / doctor123")
        print("Patient: patient1 / patient123")
        print("Receptionist: receptionist1 / receptionist123")
        print("Pharmacist: pharmacist1 / pharmacist123")


# Context processor to inject common variables
@app.context_processor
def inject_common_vars():
    user = get_current_user()
    
    if user:
        role_color = Config.ROLE_COLORS.get(user.role, '#6b7280')
        unread_count = Notification.query.filter_by(receiver_id=user.id, is_read=False).count()
        
        return {
            'user': user,
            'role_color': role_color,
            'unread_count': unread_count,
            'hospital_name': Config.HOSPITAL_NAME
        }
    
    return {
        'user': None,
        'role_color': None,
        'unread_count': 0,
        'hospital_name': Config.HOSPITAL_NAME
    }


# Routes
@app.route('/')
def index():
    """Home page - redirect to login"""
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    # Don't auto-redirect - let user login fresh to avoid cookie conflicts
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if not username or not password:
            flash('Please provide both username and password.', 'danger')
            return render_template('login.html')
        
        # Find user
        user = User.query.filter_by(username=username).first()
        
        if not user or not user.check_password(password):
            flash('Invalid username or password.', 'danger')
            return render_template('login.html')
        
        if not user.is_active:
            flash('Your account has been deactivated. Please contact the administrator.', 'danger')
            return render_template('login.html')
        
        # Store user ID in session (simpler and more reliable than JWT cookies)
        session.permanent = True
        session['user_id'] = user.id
        session['user_role'] = user.role
        
        # Redirect directly to role-specific dashboard (blueprint route)
        dashboard_routes = {
            'admin': 'admin.dashboard',
            'doctor': 'doctor.dashboard',
            'patient': 'patient.dashboard',
            'receptionist': 'receptionist.dashboard',
            'pharmacist': 'pharmacist.dashboard'
        }
        
        flash(f'Welcome back, {user.username}!', 'success')
        return redirect(url_for(dashboard_routes.get(user.role, 'login')))
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('login'))


# Role-specific login routes (redirect to main login)
@app.route('/patient/login')
@app.route('/doctor/login')
@app.route('/receptionist/login')
@app.route('/pharmacist/login')
@app.route('/admin/login')
def role_login():
    """Redirect role-specific login URLs to main login"""
    return redirect(url_for('login'))


# Redirect routes for each role
@app.route('/admin_dashboard')
def admin_dashboard():
    return redirect(url_for('admin.dashboard'))


@app.route('/doctor_dashboard')
def doctor_dashboard():
    return redirect(url_for('doctor.dashboard'))


@app.route('/patient_dashboard')
def patient_dashboard():
    return redirect(url_for('patient.dashboard'))


@app.route('/receptionist_dashboard')
def receptionist_dashboard():
    return redirect(url_for('receptionist.dashboard'))


@app.route('/pharmacist_dashboard')
def pharmacist_dashboard():
    return redirect(url_for('pharmacist.dashboard'))


# API Routes
@app.route('/api/chatbot', methods=['POST'])
def chatbot_api():
    """Chatbot API endpoint"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        message_type = data.get('type', 'general')
        role = data.get('role', 'patient')
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        response = process_chatbot_message(message, message_type, role)
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/notifications/<int:user_id>')
@jwt_required()
def get_notifications(user_id):
    """Get user notifications"""
    current_user = get_current_user()
    
    if current_user.id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    notifications = Notification.query.filter_by(receiver_id=user_id).order_by(Notification.created_at.desc()).limit(10).all()
    
    return jsonify({
        'notifications': [n.to_dict() for n in notifications]
    })


# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500


@app.errorhandler(403)
def forbidden_error(error):
    return render_template('errors/403.html'), 403


# JWT error handlers (for API endpoints only)
@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({'error': 'Token has expired'}), 401


@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({'error': 'Invalid token'}), 401


@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({'error': 'Authorization required'}), 401


# Template filters
@app.template_filter('datetime')
def format_datetime(value, format='%Y-%m-%d %H:%M'):
    """Format datetime objects"""
    if value is None:
        return ""
    return value.strftime(format)


@app.template_filter('date')
def format_date(value, format='%Y-%m-%d'):
    """Format date objects"""
    if value is None:
        return ""
    return value.strftime(format)


@app.template_filter('time')
def format_time(value, format='%H:%M'):
    """Format time objects"""
    if value is None:
        return ""
    return value.strftime(format)


# CLI Commands
@app.cli.command()
def init_db():
    """Initialize the database"""
    db.create_all()
    print("Database initialized!")


@app.cli.command()
def reset_db():
    """Reset the database"""
    db.drop_all()
    db.create_all()
    print("Database reset!")


if __name__ == '__main__':
    # Ensure upload directories exist
    os.makedirs('static/prescriptions', exist_ok=True)
    os.makedirs('database', exist_ok=True)
    
    # Run the application
    app.run(debug=True, host='0.0.0.0', port=5000)
