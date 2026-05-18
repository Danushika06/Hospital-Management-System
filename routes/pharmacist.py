from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from auth import role_required, get_current_user
from models import db, User, Prescription, Medicine, Notification
from datetime import datetime, date, timedelta

pharmacist_bp = Blueprint('pharmacist', __name__, url_prefix='/pharmacist')

@pharmacist_bp.route('/dashboard')
@role_required('pharmacist')
def dashboard():
    """Pharmacist dashboard"""
    current_user = get_current_user()
    
    # Get pending prescriptions
    pending_prescriptions = Prescription.query.filter_by(
        issued_status='Pending'
    ).order_by(Prescription.created_at.desc()).limit(10).all()
    
    # Get low stock medicines
    low_stock_medicines = Medicine.query.filter(Medicine.quantity < 50).order_by(Medicine.quantity).all()
    
    # Get medicines expiring soon (within 30 days)
    expiry_threshold = date.today() + timedelta(days=30)
    expiring_soon = Medicine.query.filter(
        Medicine.expiry_date <= expiry_threshold,
        Medicine.expiry_date >= date.today()
    ).order_by(Medicine.expiry_date).all()
    
    # Statistics
    total_pending = Prescription.query.filter_by(issued_status='Pending').count()
    total_dispensed = Prescription.query.filter_by(issued_status='Dispensed').count()
    total_medicines = Medicine.query.count()
    low_stock_count = len(low_stock_medicines)
    
    return render_template('pharmacist/dashboard.html',
                         user=current_user,
                         pending_prescriptions=pending_prescriptions,
                         low_stock_medicines=low_stock_medicines,
                         expiring_soon=expiring_soon,
                         total_pending=total_pending,
                         total_dispensed=total_dispensed,
                         total_medicines=total_medicines,
                         low_stock_count=low_stock_count)


@pharmacist_bp.route('/prescriptions')
@role_required('pharmacist')
def prescriptions():
    """View all prescriptions, split into Pending and Dispensed"""
    current_user = get_current_user()

    pending_prescriptions = Prescription.query.filter_by(
        issued_status='Pending'
    ).order_by(Prescription.created_at.desc()).all()

    dispensed_prescriptions = Prescription.query.filter_by(
        issued_status='Dispensed'
    ).order_by(Prescription.created_at.desc()).all()

    return render_template('pharmacist/prescriptions.html',
                         user=current_user,
                         pending_prescriptions=pending_prescriptions,
                         dispensed_prescriptions=dispensed_prescriptions)


@pharmacist_bp.route('/dispense_prescription/<int:prescription_id>', methods=['POST'])
@role_required('pharmacist')
def dispense_prescription(prescription_id):
    """Mark a prescription as dispensed"""
    try:
        prescription = Prescription.query.get_or_404(prescription_id)
        
        if prescription.issued_status == 'Dispensed':
            flash('This prescription has already been dispensed.', 'warning')
            return redirect(url_for('pharmacist.prescriptions'))
        
        prescription.issued_status = 'Dispensed'
        
        # Create notification for patient
        notification = Notification(
            receiver_id=prescription.patient_id,
            message=f'Your prescription (ID: {prescription.id}) has been dispensed and is ready for pickup.'
        )
        db.session.add(notification)
        
        db.session.commit()
        
        flash('Prescription dispensed successfully!', 'success')
        return redirect(url_for('pharmacist.prescriptions'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error dispensing prescription: {str(e)}', 'danger')
        return redirect(url_for('pharmacist.prescriptions'))


@pharmacist_bp.route('/inventory')
@role_required('pharmacist')
def inventory():
    """View medicine inventory"""
    current_user = get_current_user()
    all_medicines = Medicine.query.order_by(Medicine.name).all()
    
    return render_template('pharmacist/inventory.html', 
                         user=current_user, 
                         medicines=all_medicines,
                         today=date.today())


@pharmacist_bp.route('/add_medicine', methods=['POST'])
@role_required('pharmacist')
def add_medicine():
    """Add a new medicine to inventory"""
    try:
        name = request.form.get('name', '').strip()
        quantity = request.form.get('quantity', '').strip()
        expiry_date = request.form.get('expiry_date', '').strip()
        
        if not name or not quantity or not expiry_date:
            flash('All fields are required.', 'danger')
            return redirect(url_for('pharmacist.inventory'))
        
        # Convert to appropriate types
        quantity = int(quantity)
        expiry_date = datetime.strptime(expiry_date, '%Y-%m-%d').date()
        
        # Check if medicine already exists
        existing_medicine = Medicine.query.filter_by(name=name).first()
        if existing_medicine:
            flash('Medicine with this name already exists. Use update stock instead.', 'danger')
            return redirect(url_for('pharmacist.inventory'))
        
        # Validate expiry date
        if expiry_date < date.today():
            flash('Cannot add expired medicine.', 'danger')
            return redirect(url_for('pharmacist.inventory'))
        
        # Create new medicine
        medicine = Medicine(
            name=name,
            quantity=quantity,
            expiry_date=expiry_date
        )
        
        db.session.add(medicine)
        db.session.commit()
        
        flash(f'Medicine {name} added successfully!', 'success')
        return redirect(url_for('pharmacist.inventory'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error adding medicine: {str(e)}', 'danger')
        return redirect(url_for('pharmacist.inventory'))


@pharmacist_bp.route('/update_stock/<int:medicine_id>', methods=['POST'])
@role_required('pharmacist')
def update_stock(medicine_id):
    """Update medicine stock"""
    try:
        medicine = Medicine.query.get_or_404(medicine_id)
        
        new_quantity = request.form.get('quantity', '').strip()
        
        if not new_quantity:
            flash('Quantity is required.', 'danger')
            return redirect(url_for('pharmacist.inventory'))
        
        new_quantity = int(new_quantity)
        
        if new_quantity < 0:
            flash('Quantity cannot be negative.', 'danger')
            return redirect(url_for('pharmacist.inventory'))
        
        medicine.quantity = new_quantity
        db.session.commit()
        
        flash(f'Stock updated for {medicine.name}!', 'success')
        return redirect(url_for('pharmacist.inventory'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating stock: {str(e)}', 'danger')
        return redirect(url_for('pharmacist.inventory'))


@pharmacist_bp.route('/restock_medicine/<int:medicine_id>', methods=['POST'])
@role_required('pharmacist')
def restock_medicine(medicine_id):
    """Add quantity to an existing medicine's stock"""
    try:
        medicine = Medicine.query.get_or_404(medicine_id)

        add_quantity = request.form.get('quantity', '').strip()

        if not add_quantity:
            flash('Quantity is required.', 'danger')
            return redirect(url_for('pharmacist.low_stock_alerts'))

        add_quantity = int(add_quantity)

        if add_quantity < 1:
            flash('Restock quantity must be at least 1.', 'danger')
            return redirect(url_for('pharmacist.low_stock_alerts'))

        medicine.quantity += add_quantity
        db.session.commit()

        flash(f'Restocked {medicine.name} (+{add_quantity}). New stock: {medicine.quantity} units.', 'success')
        return redirect(url_for('pharmacist.low_stock_alerts'))

    except Exception as e:
        db.session.rollback()
        flash(f'Error restocking medicine: {str(e)}', 'danger')
        return redirect(url_for('pharmacist.low_stock_alerts'))


@pharmacist_bp.route('/delete_medicine/<int:medicine_id>', methods=['POST'])
@role_required('pharmacist')
def delete_medicine(medicine_id):
    """Delete a medicine from inventory"""
    try:
        medicine = Medicine.query.get_or_404(medicine_id)
        
        medicine_name = medicine.name
        db.session.delete(medicine)
        db.session.commit()
        
        flash(f'Medicine {medicine_name} deleted from inventory.', 'success')
        return redirect(url_for('pharmacist.inventory'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting medicine: {str(e)}', 'danger')
        return redirect(url_for('pharmacist.inventory'))


@pharmacist_bp.route('/dispensing_history')
@role_required('pharmacist')
def dispensing_history():
    """View dispensing history"""
    current_user = get_current_user()
    dispensed_prescriptions = Prescription.query.filter_by(
        issued_status='Dispensed'
    ).order_by(Prescription.created_at.desc()).all()
    
    return render_template('pharmacist/dispensing_history.html', 
                         user=current_user, 
                         prescriptions=dispensed_prescriptions)


@pharmacist_bp.route('/low_stock_alerts')
@role_required('pharmacist')
def low_stock_alerts():
    """View low stock alerts"""
    current_user = get_current_user()
    low_stock_medicines = Medicine.query.filter(Medicine.quantity < 50).order_by(Medicine.quantity).all()
    
    return render_template('pharmacist/low_stock_alerts.html', 
                         user=current_user, 
                         low_stock_medicines=low_stock_medicines)


@pharmacist_bp.route('/expiry_tracking')
@role_required('pharmacist')
def expiry_tracking():
    """View expiry tracking"""
    current_user = get_current_user()
    today = date.today()
    
    # Get all medicines
    all_medicines = Medicine.query.order_by(Medicine.expiry_date).all()
    
    # Get expired medicines
    expired_medicines = Medicine.query.filter(
        Medicine.expiry_date < today
    ).order_by(Medicine.expiry_date).all()
    
    # Get medicines expiring within 30 days
    expiry_threshold = today + timedelta(days=30)
    expiring_soon_medicines = Medicine.query.filter(
        Medicine.expiry_date >= today,
        Medicine.expiry_date <= expiry_threshold
    ).order_by(Medicine.expiry_date).all()
    
    # Calculate counts
    expired_count = len(expired_medicines)
    expiring_soon_count = len(expiring_soon_medicines)
    good_count = len(all_medicines) - expired_count - expiring_soon_count
    
    return render_template('pharmacist/expiry_tracking.html', 
                         user=current_user, 
                         medicines=all_medicines,
                         expired_medicines=expired_medicines,
                         expiring_soon_medicines=expiring_soon_medicines,
                         expired_count=expired_count,
                         expiring_soon_count=expiring_soon_count,
                         good_count=good_count,
                         today=today)


@pharmacist_bp.route('/notifications')
@role_required('pharmacist')
def notifications():
    """View pharmacist notifications"""
    current_user = get_current_user()
    
    notifications = Notification.query.filter_by(
        receiver_id=current_user.id
    ).order_by(Notification.created_at.desc()).all()
    
    return render_template('pharmacist/notifications.html',
                         user=current_user,
                         notifications=notifications)


@pharmacist_bp.route('/notifications/mark_read/<int:notification_id>', methods=['POST'])
@role_required('pharmacist')
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
