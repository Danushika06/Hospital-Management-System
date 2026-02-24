from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    """User model for all roles"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, index=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    appointments_as_patient = db.relationship('Appointment', foreign_keys='Appointment.patient_id', 
                                             backref='patient', lazy=True, cascade='all, delete-orphan')
    appointments_as_doctor = db.relationship('Appointment', foreign_keys='Appointment.doctor_id', 
                                            backref='doctor', lazy=True)
    prescriptions_as_patient = db.relationship('Prescription', foreign_keys='Prescription.patient_id',
                                              backref='patient', lazy=True)
    prescriptions_as_doctor = db.relationship('Prescription', foreign_keys='Prescription.doctor_id',
                                             backref='doctor', lazy=True)
    notifications = db.relationship('Notification', backref='receiver', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')
    
    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def __repr__(self):
        return f'<User {self.username} ({self.role})>'


class Appointment(db.Model):
    """Appointment model"""
    __tablename__ = 'appointments'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, index=True)
    time = db.Column(db.Time, nullable=False)
    status = db.Column(db.String(20), default='Pending', nullable=False, index=True)  # Pending/Approved/Rejected/Completed
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    prescriptions = db.relationship('Prescription', backref='appointment', lazy=True)
    
    def to_dict(self):
        """Convert appointment to dictionary"""
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'patient_name': self.patient.username if self.patient else 'Unknown',
            'doctor_id': self.doctor_id,
            'doctor_name': self.doctor.username if self.doctor else 'Unknown',
            'date': self.date.strftime('%Y-%m-%d'),
            'time': self.time.strftime('%H:%M'),
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def __repr__(self):
        return f'<Appointment {self.id} - {self.status}>'


class Prescription(db.Model):
    """Prescription model"""
    __tablename__ = 'prescriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'), nullable=False, index=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    diagnosis = db.Column(db.Text, nullable=False)
    medicine_details = db.Column(db.Text, nullable=False)  # JSON string of medicines
    issued_status = db.Column(db.String(20), default='Pending', nullable=False, index=True)  # Pending/Dispensed
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        """Convert prescription to dictionary"""
        return {
            'id': self.id,
            'appointment_id': self.appointment_id,
            'doctor_id': self.doctor_id,
            'doctor_name': self.doctor.username if self.doctor else 'Unknown',
            'patient_id': self.patient_id,
            'patient_name': self.patient.username if self.patient else 'Unknown',
            'diagnosis': self.diagnosis,
            'medicine_details': self.medicine_details,
            'issued_status': self.issued_status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def __repr__(self):
        return f'<Prescription {self.id} - {self.issued_status}>'


class Medicine(db.Model):
    """Medicine inventory model"""
    __tablename__ = 'medicines'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True, index=True)
    quantity = db.Column(db.Integer, default=0, nullable=False)
    expiry_date = db.Column(db.Date, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        """Convert medicine to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'quantity': self.quantity,
            'expiry_date': self.expiry_date.strftime('%Y-%m-%d'),
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def is_low_stock(self, threshold=50):
        """Check if medicine is low on stock"""
        return self.quantity < threshold
    
    def is_expired(self):
        """Check if medicine is expired"""
        return self.expiry_date < datetime.utcnow().date()
    
    def __repr__(self):
        return f'<Medicine {self.name} - Qty: {self.quantity}>'


class Notification(db.Model):
    """Notification model"""
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    def to_dict(self):
        """Convert notification to dictionary"""
        return {
            'id': self.id,
            'receiver_id': self.receiver_id,
            'message': self.message,
            'is_read': self.is_read,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def __repr__(self):
        return f'<Notification {self.id} - Read: {self.is_read}>'
