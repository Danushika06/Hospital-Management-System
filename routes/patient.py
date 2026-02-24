from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, send_file
from auth import role_required, get_current_user
from models import db, User, Appointment, Prescription, Notification
from services.pdf_service import generate_prescription_pdf
from datetime import datetime, date, timedelta
import json
import os

patient_bp = Blueprint('patient', __name__, url_prefix='/patient')

@patient_bp.route('/dashboard')
@role_required('patient')
def dashboard():
    """Patient dashboard"""
    current_user = get_current_user()
    
    # Get upcoming appointments
    today = date.today()
    upcoming_appointments = Appointment.query.filter(
        Appointment.patient_id == current_user.id,
        Appointment.date >= today
    ).order_by(Appointment.date, Appointment.time).limit(5).all()
    
    # Get recent prescriptions
    recent_prescriptions = Prescription.query.filter_by(
        patient_id=current_user.id
    ).order_by(Prescription.created_at.desc()).limit(5).all()
    
    # Get statistics
    total_appointments = Appointment.query.filter_by(patient_id=current_user.id).count()
    total_prescriptions = Prescription.query.filter_by(patient_id=current_user.id).count()
    pending_appointments = Appointment.query.filter_by(
        patient_id=current_user.id,
        status='Pending'
    ).count()
    
    # Get unread notifications
    unread_notifications = Notification.query.filter_by(
        receiver_id=current_user.id,
        is_read=False
    ).order_by(Notification.created_at.desc()).limit(5).all()
    
    return render_template('patient/dashboard.html',
                         user=current_user,
                         upcoming_appointments=upcoming_appointments,
                         recent_prescriptions=recent_prescriptions,
                         total_appointments=total_appointments,
                         total_prescriptions=total_prescriptions,
                         pending_appointments=pending_appointments,
                         unread_notifications=unread_notifications)


@patient_bp.route('/book_appointment', methods=['GET', 'POST'])
@role_required('patient')
def book_appointment():
    """Book a new appointment"""
    current_user = get_current_user()
    
    if request.method == 'POST':
        try:
            doctor_id = request.form.get('doctor_id', '').strip()
            appointment_date = request.form.get('date', '').strip()
            appointment_time = request.form.get('time', '').strip()
            notes = request.form.get('notes', '').strip()
            
            if not doctor_id or not appointment_date or not appointment_time:
                flash('Doctor, date, and time are required.', 'danger')
                return redirect(url_for('patient.book_appointment'))
            
            # Convert to appropriate types
            doctor_id = int(doctor_id)
            appointment_date = datetime.strptime(appointment_date, '%Y-%m-%d').date()
            appointment_time = datetime.strptime(appointment_time, '%H:%M').time()
            
            # Validate doctor exists
            doctor = User.query.get(doctor_id)
            if not doctor or doctor.role != 'doctor' or not doctor.is_active:
                flash('Invalid doctor selected.', 'danger')
                return redirect(url_for('patient.book_appointment'))
            
            # Check if appointment is in the past
            if appointment_date < date.today():
                flash('Cannot book appointments in the past.', 'danger')
                return redirect(url_for('patient.book_appointment'))
            
            # Create appointment
            appointment = Appointment(
                patient_id=current_user.id,
                doctor_id=doctor_id,
                date=appointment_date,
                time=appointment_time,
                status='Pending',
                notes=notes
            )
            
            db.session.add(appointment)
            
            # Create notification for receptionist
            receptionists = User.query.filter_by(role='receptionist', is_active=True).all()
            for receptionist in receptionists:
                notification = Notification(
                    receiver_id=receptionist.id,
                    message=f'{current_user.username} has booked an appointment with Dr. {doctor.username}.'
                )
                db.session.add(notification)
            
            db.session.commit()
            
            flash('Appointment booked successfully! Waiting for approval.', 'success')
            return redirect(url_for('patient.appointments'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error booking appointment: {str(e)}', 'danger')
            return redirect(url_for('patient.book_appointment'))
    
    # Get all active doctors
    doctors = User.query.filter_by(role='doctor', is_active=True).order_by(User.username).all()
    
    return render_template('patient/book_appointment.html', user=current_user, doctors=doctors)


@patient_bp.route('/appointments')
@role_required('patient')
def appointments():
    """View appointment history"""
    current_user = get_current_user()
    all_appointments = Appointment.query.filter_by(
        patient_id=current_user.id
    ).order_by(Appointment.date.desc(), Appointment.time.desc()).all()
    
    return render_template('patient/appointments.html', user=current_user, appointments=all_appointments)


@patient_bp.route('/prescriptions')
@role_required('patient')
def prescriptions():
    """View prescriptions"""
    current_user = get_current_user()
    all_prescriptions = Prescription.query.filter_by(
        patient_id=current_user.id
    ).order_by(Prescription.created_at.desc()).all()
    
    return render_template('patient/prescriptions.html', user=current_user, prescriptions=all_prescriptions)


@patient_bp.route('/download_prescription/<int:prescription_id>')
@role_required('patient')
def download_prescription(prescription_id):
    """Download prescription as PDF"""
    current_user = get_current_user()
    prescription = Prescription.query.get_or_404(prescription_id)
    
    # Verify this is the patient's prescription
    if prescription.patient_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('patient.prescriptions'))
    
    try:
        # Generate PDF
        pdf_path = generate_prescription_pdf(prescription)
        
        if os.path.exists(pdf_path):
            return send_file(pdf_path, as_attachment=True, download_name=f'prescription_{prescription.id}.pdf')
        else:
            flash('Error generating PDF.', 'danger')
            return redirect(url_for('patient.prescriptions'))
            
    except Exception as e:
        flash(f'Error downloading prescription: {str(e)}', 'danger')
        return redirect(url_for('patient.prescriptions'))


@patient_bp.route('/analytics')
@role_required('patient')
def analytics():
    """View medical analytics"""
    current_user = get_current_user()
    
    # Get statistics
    total_appointments = Appointment.query.filter_by(
        patient_id=current_user.id
    ).count()
    
    # Get all prescriptions
    all_prescriptions = Prescription.query.filter_by(patient_id=current_user.id).all()
    total_prescriptions = len(all_prescriptions)
    
    # Count medicine frequency
    medicine_frequency = {}
    for prescription in all_prescriptions:
        medicines = prescription.medicine_details.split('\n')
        for medicine in medicines:
            medicine = medicine.strip()
            if medicine:
                medicine_frequency[medicine] = medicine_frequency.get(medicine, 0) + 1
    
    # Get most frequent medicines and unique count
    frequent_medicines = sorted(medicine_frequency.items(), key=lambda x: x[1], reverse=True)[:5]
    unique_medicines = len(medicine_frequency)
    
    # Get appointments by month (last 6 months)
    appointments_by_month = []
    for i in range(6):
        target_date = date.today() - timedelta(days=30*i)
        month_start = target_date.replace(day=1)
        if i == 0:
            month_end = date.today()
        else:
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        count = Appointment.query.filter(
            Appointment.patient_id == current_user.id,
            Appointment.date >= month_start,
            Appointment.date <= month_end
        ).count()
        
        appointments_by_month.append({
            'month': month_start.strftime('%b %Y'),
            'count': count
        })
    
    appointments_by_month.reverse()
    
    return render_template('patient/analytics.html',
                         user=current_user,
                         total_appointments=total_appointments,
                         total_prescriptions=total_prescriptions,
                         unique_medicines=unique_medicines,
                         frequent_medicines=frequent_medicines,
                         appointments_by_month=appointments_by_month)


@patient_bp.route('/chatbot')
@role_required('patient')
def chatbot():
    """AI Chatbot page"""
    current_user = get_current_user()
    return render_template('patient/chatbot.html', user=current_user)


@patient_bp.route('/profile')
@role_required('patient')
def profile():
    """View profile"""
    current_user = get_current_user()
    return render_template('patient/profile.html', user=current_user)


@patient_bp.route('/notifications')
@role_required('patient')
def notifications():
    """View notifications"""
    current_user = get_current_user()
    all_notifications = Notification.query.filter_by(
        receiver_id=current_user.id
    ).order_by(Notification.created_at.desc()).all()
    
    return render_template('patient/notifications.html', user=current_user, notifications=all_notifications)


@patient_bp.route('/mark_notification_read/<int:notification_id>', methods=['POST'])
@role_required('patient')
def mark_notification_read(notification_id):
    """Mark notification as read"""
    current_user = get_current_user()
    notification = Notification.query.get_or_404(notification_id)
    
    if notification.receiver_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('patient.notifications'))
    
    notification.is_read = True
    db.session.commit()
    
    return redirect(url_for('patient.notifications'))
