from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from auth import role_required, get_current_user
from models import db, User, Appointment, Notification
from datetime import datetime, date

receptionist_bp = Blueprint('receptionist', __name__, url_prefix='/receptionist')

@receptionist_bp.route('/dashboard')
@role_required('receptionist')
def dashboard():
    """Receptionist dashboard"""
    current_user = get_current_user()
    
    # Get pending appointments
    pending_appointments = Appointment.query.filter_by(
        status='Pending'
    ).order_by(Appointment.date, Appointment.time).all()
    
    # Today's appointments
    today = date.today()
    todays_appointments = Appointment.query.filter_by(
        date=today
    ).order_by(Appointment.time).all()
    
    # Statistics
    total_pending = Appointment.query.filter_by(status='Pending').count()
    total_approved = Appointment.query.filter_by(status='Approved').count()
    total_today = Appointment.query.filter_by(date=today).count()
    
    return render_template('receptionist/dashboard.html',
                         user=current_user,
                         pending_appointments=pending_appointments,
                         todays_appointments=todays_appointments,
                         total_pending=total_pending,
                         total_approved=total_approved,
                         total_today=total_today)


@receptionist_bp.route('/appointments')
@role_required('receptionist')
def appointments():
    """View all appointments"""
    current_user = get_current_user()
    all_appointments = Appointment.query.order_by(
        Appointment.date.desc(), 
        Appointment.time.desc()
    ).all()
    
    return render_template('receptionist/appointments.html', 
                         user=current_user, 
                         appointments=all_appointments)


@receptionist_bp.route('/approve_appointment/<int:appointment_id>', methods=['POST'])
@role_required('receptionist')
def approve_appointment(appointment_id):
    """Approve an appointment"""
    try:
        appointment = Appointment.query.get_or_404(appointment_id)
        
        if appointment.status != 'Pending':
            flash('This appointment has already been processed.', 'warning')
            return redirect(url_for('receptionist.dashboard'))
        
        appointment.status = 'Approved'
        
        # Create notification for patient
        notification = Notification(
            receiver_id=appointment.patient_id,
            message=f'Your appointment with Dr. {appointment.doctor.username} on {appointment.date.strftime("%Y-%m-%d")} has been approved.'
        )
        db.session.add(notification)
        
        # Create notification for doctor
        doctor_notification = Notification(
            receiver_id=appointment.doctor_id,
            message=f'New appointment scheduled with {appointment.patient.username} on {appointment.date.strftime("%Y-%m-%d")} at {appointment.time.strftime("%H:%M")}.'
        )
        db.session.add(doctor_notification)
        
        db.session.commit()
        
        flash('Appointment approved successfully!', 'success')
        return redirect(url_for('receptionist.dashboard'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error approving appointment: {str(e)}', 'danger')
        return redirect(url_for('receptionist.dashboard'))


@receptionist_bp.route('/reject_appointment/<int:appointment_id>', methods=['POST'])
@role_required('receptionist')
def reject_appointment(appointment_id):
    """Reject an appointment"""
    try:
        appointment = Appointment.query.get_or_404(appointment_id)
        
        if appointment.status != 'Pending':
            flash('This appointment has already been processed.', 'warning')
            return redirect(url_for('receptionist.dashboard'))
        
        appointment.status = 'Rejected'
        
        # Create notification for patient
        notification = Notification(
            receiver_id=appointment.patient_id,
            message=f'Your appointment with Dr. {appointment.doctor.username} on {appointment.date.strftime("%Y-%m-%d")} has been rejected. Please contact reception for more information.'
        )
        db.session.add(notification)
        
        db.session.commit()
        
        flash('Appointment rejected.', 'success')
        return redirect(url_for('receptionist.dashboard'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error rejecting appointment: {str(e)}', 'danger')
        return redirect(url_for('receptionist.dashboard'))


@receptionist_bp.route('/reschedule_appointment/<int:appointment_id>', methods=['POST'])
@role_required('receptionist')
def reschedule_appointment(appointment_id):
    """Reschedule an appointment"""
    try:
        appointment = Appointment.query.get_or_404(appointment_id)
        
        new_date = request.form.get('new_date', '').strip()
        new_time = request.form.get('new_time', '').strip()
        
        if not new_date or not new_time:
            flash('Date and time are required.', 'danger')
            return redirect(url_for('receptionist.appointments'))
        
        # Convert to appropriate types
        new_date = datetime.strptime(new_date, '%Y-%m-%d').date()
        new_time = datetime.strptime(new_time, '%H:%M').time()
        
        # Check if appointment is in the past
        if new_date < date.today():
            flash('Cannot reschedule appointments to past dates.', 'danger')
            return redirect(url_for('receptionist.appointments'))
        
        old_date = appointment.date
        old_time = appointment.time
        
        appointment.date = new_date
        appointment.time = new_time
        
        # Create notification for patient
        notification = Notification(
            receiver_id=appointment.patient_id,
            message=f'Your appointment with Dr. {appointment.doctor.username} has been rescheduled from {old_date.strftime("%Y-%m-%d")} {old_time.strftime("%H:%M")} to {new_date.strftime("%Y-%m-%d")} {new_time.strftime("%H:%M")}.'
        )
        db.session.add(notification)
        
        # Create notification for doctor
        doctor_notification = Notification(
            receiver_id=appointment.doctor_id,
            message=f'Appointment with {appointment.patient.username} has been rescheduled to {new_date.strftime("%Y-%m-%d")} at {new_time.strftime("%H:%M")}.'
        )
        db.session.add(doctor_notification)
        
        db.session.commit()
        
        flash('Appointment rescheduled successfully!', 'success')
        return redirect(url_for('receptionist.appointments'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error rescheduling appointment: {str(e)}', 'danger')
        return redirect(url_for('receptionist.appointments'))


@receptionist_bp.route('/queue')
@role_required('receptionist')
def queue():
    """View daily queue"""
    current_user = get_current_user()
    today = date.today()
    
    todays_queue = Appointment.query.filter_by(
        date=today,
        status='Approved'
    ).order_by(Appointment.time).all()
    
    return render_template('receptionist/queue.html', 
                         user=current_user, 
                         queue=todays_queue, 
                         today=today)


@receptionist_bp.route('/notify_doctor/<int:doctor_id>', methods=['POST'])
@role_required('receptionist')
def notify_doctor(doctor_id):
    """Send notification to a doctor"""
    try:
        doctor = User.query.get_or_404(doctor_id)
        
        if doctor.role != 'doctor':
            flash('Invalid doctor ID.', 'danger')
            return redirect(url_for('receptionist.dashboard'))
        
        message = request.form.get('message', '').strip()
        
        if not message:
            flash('Message cannot be empty.', 'danger')
            return redirect(url_for('receptionist.dashboard'))
        
        notification = Notification(
            receiver_id=doctor_id,
            message=f'Message from Reception: {message}'
        )
        db.session.add(notification)
        db.session.commit()
        
        flash(f'Notification sent to Dr. {doctor.username}!', 'success')
        return redirect(url_for('receptionist.dashboard'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error sending notification: {str(e)}', 'danger')
        return redirect(url_for('receptionist.dashboard'))


@receptionist_bp.route('/notifications')
@role_required('receptionist')
def notifications():
    """View receptionist notifications"""
    current_user = get_current_user()
    
    notifications = Notification.query.filter_by(
        receiver_id=current_user.id
    ).order_by(Notification.created_at.desc()).all()
    
    return render_template('receptionist/notifications.html',
                         user=current_user,
                         notifications=notifications)


@receptionist_bp.route('/notifications/mark_read/<int:notification_id>', methods=['POST'])
@role_required('receptionist')
def mark_notification_read(notification_id):
    """Mark a notification as read"""
    current_user = get_current_user()
    
    notification = Notification.query.filter_by(
        id=notification_id,
        receiver_id=current_user.id
    ).first_or_404()
    
    notification.is_read = True
    db.session.commit()
    
    return jsonify({'success': True})
