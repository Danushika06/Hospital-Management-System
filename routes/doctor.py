from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, send_file
from auth import role_required, get_current_user
from models import db, User, Appointment, Prescription, Notification
from services.pdf_service import generate_prescription_pdf
from datetime import datetime, date
import json

doctor_bp = Blueprint('doctor', __name__, url_prefix='/doctor')

@doctor_bp.route('/dashboard')
@role_required('doctor')
def dashboard():
    """Doctor dashboard"""
    current_user = get_current_user()
    
    # Get today's approved appointments
    today = date.today()
    todays_appointments = Appointment.query.filter_by(
        doctor_id=current_user.id,
        date=today,
        status='Approved'
    ).order_by(Appointment.time).all()
    
    # Get all approved appointments
    approved_appointments = Appointment.query.filter_by(
        doctor_id=current_user.id,
        status='Approved'
    ).order_by(Appointment.date.desc(), Appointment.time.desc()).limit(20).all()
    
    # Get prescription stats
    total_prescriptions = Prescription.query.filter_by(doctor_id=current_user.id).count()
    pending_prescriptions = Prescription.query.filter_by(
        doctor_id=current_user.id,
        issued_status='Pending'
    ).count()
    
    # Get unread notifications
    unread_notifications = Notification.query.filter_by(
        receiver_id=current_user.id,
        is_read=False
    ).order_by(Notification.created_at.desc()).limit(5).all()
    
    return render_template('doctor/dashboard.html',
                         user=current_user,
                         todays_appointments=todays_appointments,
                         approved_appointments=approved_appointments,
                         total_prescriptions=total_prescriptions,
                         pending_prescriptions=pending_prescriptions,
                         unread_notifications=unread_notifications)


@doctor_bp.route('/appointments')
@role_required('doctor')
def appointments():
    """View all approved appointments"""
    current_user = get_current_user()
    all_appointments = Appointment.query.filter_by(
        doctor_id=current_user.id,
        status='Approved'
    ).order_by(Appointment.date.desc(), Appointment.time.desc()).all()
    
    return render_template('doctor/appointments.html', user=current_user, appointments=all_appointments)


@doctor_bp.route('/patient_history/<int:patient_id>')
@role_required('doctor')
def patient_history(patient_id):
    """View patient history"""
    current_user = get_current_user()
    patient = User.query.get_or_404(patient_id)
    
    if patient.role != 'patient':
        flash('Invalid patient ID.', 'danger')
        return redirect(url_for('doctor.dashboard'))
    
    # Get patient's appointments with this doctor
    appointments = Appointment.query.filter_by(
        patient_id=patient_id,
        doctor_id=current_user.id
    ).order_by(Appointment.date.desc()).all()
    
    # Get patient's prescriptions from this doctor
    prescriptions = Prescription.query.filter_by(
        patient_id=patient_id,
        doctor_id=current_user.id
    ).order_by(Prescription.created_at.desc()).all()
    
    return render_template('doctor/patient_history.html',
                         user=current_user,
                         patient=patient,
                         appointments=appointments,
                         prescriptions=prescriptions)


@doctor_bp.route('/issue_prescription/<int:appointment_id>', methods=['GET', 'POST'])
@role_required('doctor')
def issue_prescription(appointment_id):
    """Issue a prescription for an appointment"""
    current_user = get_current_user()
    appointment = Appointment.query.get_or_404(appointment_id)
    
    # Verify this is the doctor's appointment
    if appointment.doctor_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('doctor.dashboard'))
    
    if request.method == 'POST':
        try:
            diagnosis = request.form.get('diagnosis', '').strip()
            medicines = request.form.get('medicines', '').strip()
            
            if not diagnosis or not medicines:
                flash('Diagnosis and medicines are required.', 'danger')
                return redirect(url_for('doctor.issue_prescription', appointment_id=appointment_id))
            
            # Create prescription
            prescription = Prescription(
                appointment_id=appointment.id,
                doctor_id=current_user.id,
                patient_id=appointment.patient_id,
                diagnosis=diagnosis,
                medicine_details=medicines,
                issued_status='Pending'
            )
            
            db.session.add(prescription)
            
            # Update appointment status to completed
            appointment.status = 'Completed'
            
            # Create notification for patient
            notification = Notification(
                receiver_id=appointment.patient_id,
                message=f'Dr. {current_user.username} has issued a prescription for your appointment.'
            )
            db.session.add(notification)
            
            # Create notification for pharmacist
            pharmacists = User.query.filter_by(role='pharmacist', is_active=True).all()
            for pharmacist in pharmacists:
                notif = Notification(
                    receiver_id=pharmacist.id,
                    message=f'New prescription issued by Dr. {current_user.username} for {appointment.patient.username}.'
                )
                db.session.add(notif)
            
            db.session.commit()
            
            flash('Prescription issued successfully!', 'success')
            return redirect(url_for('doctor.dashboard'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error issuing prescription: {str(e)}', 'danger')
            return redirect(url_for('doctor.issue_prescription', appointment_id=appointment_id))
    
    return render_template('doctor/issue_prescription.html', user=current_user, appointment=appointment)


@doctor_bp.route('/prescriptions')
@role_required('doctor')
def prescriptions():
    """View all prescriptions issued by doctor"""
    current_user = get_current_user()
    all_prescriptions = Prescription.query.filter_by(
        doctor_id=current_user.id
    ).order_by(Prescription.created_at.desc()).all()
    
    return render_template('doctor/prescriptions.html', user=current_user, prescriptions=all_prescriptions)


@doctor_bp.route('/notifications')
@role_required('doctor')
def notifications():
    """View notifications"""
    current_user = get_current_user()
    all_notifications = Notification.query.filter_by(
        receiver_id=current_user.id
    ).order_by(Notification.created_at.desc()).all()
    
    return render_template('doctor/notifications.html', user=current_user, notifications=all_notifications)


@doctor_bp.route('/mark_notification_read/<int:notification_id>', methods=['POST'])
@role_required('doctor')
def mark_notification_read(notification_id):
    """Mark notification as read"""
    current_user = get_current_user()
    notification = Notification.query.get_or_404(notification_id)
    
    if notification.receiver_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('doctor.notifications'))
    
    notification.is_read = True
    db.session.commit()
    
    return redirect(url_for('doctor.notifications'))
