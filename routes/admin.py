from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from auth import role_required, get_current_user
from models import db, User, Appointment, Prescription, Medicine, Notification
from datetime import datetime, date
import json
import shutil
import os

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard')
@role_required('admin')
def dashboard():
    """Admin dashboard with statistics"""
    current_user = get_current_user()
    
    # Get statistics
    total_patients = User.query.filter_by(role='patient', is_active=True).count()
    total_doctors = User.query.filter_by(role='doctor', is_active=True).count()
    total_pharmacists = User.query.filter_by(role='pharmacist', is_active=True).count()
    
    # Appointments today
    today = date.today()
    appointments_today = Appointment.query.filter_by(date=today).count()
    
    # Total prescriptions
    total_prescriptions = Prescription.query.count()
    
    # Pending appointments
    pending_appointments = Appointment.query.filter_by(status='Pending').count()
    
    # Get all users
    all_users = User.query.order_by(User.created_at.desc()).all()
    
    # Get recent appointments
    recent_appointments = Appointment.query.order_by(Appointment.created_at.desc()).limit(10).all()
    
    # Get recent prescriptions
    recent_prescriptions = Prescription.query.order_by(Prescription.created_at.desc()).limit(10).all()
    
    return render_template('admin/dashboard.html',
                         user=current_user,
                         total_patients=total_patients,
                         total_doctors=total_doctors,
                         total_pharmacists=total_pharmacists,
                         appointments_today=appointments_today,
                         total_prescriptions=total_prescriptions,
                         pending_appointments=pending_appointments,
                         all_users=all_users,
                         recent_appointments=recent_appointments,
                         recent_prescriptions=recent_prescriptions)


@admin_bp.route('/users')
@role_required('admin')
def users():
    """View all users"""
    current_user = get_current_user()
    all_users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', user=current_user, all_users=all_users)


@admin_bp.route('/add_user', methods=['POST'])
@role_required('admin')
def add_user():
    """Add a new user"""
    try:
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        role = request.form.get('role', '').strip()
        
        # Validate input
        if not username or not email or not password or not role:
            flash('All fields are required.', 'danger')
            return redirect(url_for('admin.users'))
        
        if role not in ['admin', 'doctor', 'patient', 'receptionist', 'pharmacist']:
            flash('Invalid role specified.', 'danger')
            return redirect(url_for('admin.users'))
        
        # Check if user exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'danger')
            return redirect(url_for('admin.users'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists.', 'danger')
            return redirect(url_for('admin.users'))
        
        # Create new user
        new_user = User(username=username, email=email, role=role, is_active=True)
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash(f'User {username} added successfully!', 'success')
        return redirect(url_for('admin.users'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error adding user: {str(e)}', 'danger')
        return redirect(url_for('admin.users'))


@admin_bp.route('/deactivate_user/<int:user_id>', methods=['POST'])
@role_required('admin')
def deactivate_user(user_id):
    """Deactivate a user"""
    try:
        user = User.query.get_or_404(user_id)
        
        # Prevent deactivating yourself
        current_user = get_current_user()
        if user.id == current_user.id:
            flash('You cannot deactivate yourself.', 'danger')
            return redirect(url_for('admin.users'))
        
        user.is_active = not user.is_active
        db.session.commit()
        
        status = 'activated' if user.is_active else 'deactivated'
        flash(f'User {user.username} has been {status}.', 'success')
        return redirect(url_for('admin.users'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating user: {str(e)}', 'danger')
        return redirect(url_for('admin.users'))


@admin_bp.route('/delete_user/<int:user_id>', methods=['POST'])
@role_required('admin')
def delete_user(user_id):
    """Delete a user"""
    try:
        user = User.query.get_or_404(user_id)
        
        # Prevent deleting yourself
        current_user = get_current_user()
        if user.id == current_user.id:
            flash('You cannot delete yourself.', 'danger')
            return redirect(url_for('admin.users'))
        
        username = user.username
        db.session.delete(user)
        db.session.commit()
        
        flash(f'User {username} has been deleted.', 'success')
        return redirect(url_for('admin.users'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting user: {str(e)}', 'danger')
        return redirect(url_for('admin.users'))


@admin_bp.route('/appointments')
@role_required('admin')
def appointments():
    """View all appointments"""
    current_user = get_current_user()
    all_appointments = Appointment.query.order_by(Appointment.date.desc(), Appointment.time.desc()).all()
    return render_template('admin/appointments.html', user=current_user, appointments=all_appointments)


@admin_bp.route('/prescriptions')
@role_required('admin')
def prescriptions():
    """View all prescriptions"""
    current_user = get_current_user()
    all_prescriptions = Prescription.query.order_by(Prescription.created_at.desc()).all()
    return render_template('admin/prescriptions.html', user=current_user, prescriptions=all_prescriptions)


@admin_bp.route('/backup_database', methods=['POST'])
@role_required('admin')
def backup_database():
    """Create a database backup"""
    try:
        db_path = 'database/hospital.db'
        backup_path = f'database/hospital_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
        
        if os.path.exists(db_path):
            shutil.copy2(db_path, backup_path)
            flash(f'Database backed up successfully to {backup_path}', 'success')
        else:
            flash('Database file not found.', 'danger')
        
        return redirect(url_for('admin.dashboard'))
        
    except Exception as e:
        flash(f'Error creating backup: {str(e)}', 'danger')
        return redirect(url_for('admin.dashboard'))
