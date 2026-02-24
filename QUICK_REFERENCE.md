# Hospital Management System - Quick Reference Guide

## 🚀 Quick Start

### Default Login Credentials
```
Admin:        admin / admin123
Doctor:       doctor1 / doctor123
Patient:      patient1 / patient123
Receptionist: receptionist1 / receptionist123
Pharmacist:   pharmacist1 / pharmacist123
```

### Run the Application
```powershell
# Activate virtual environment (if using)
.\venv\Scripts\Activate.ps1

# Run the application
python app.py

# Access at: http://localhost:5000
```

---

## 📋 User Roles Quick Reference

| Role | Key Functions | Primary Routes |
|------|--------------|----------------|
| **Admin** | User management, system oversight | `/admin/*` |
| **Doctor** | View appointments, issue prescriptions | `/doctor/*` |
| **Patient** | Book appointments, view prescriptions, chatbot | `/patient/*` |
| **Receptionist** | Approve/reject appointments, manage queue | `/receptionist/*` |
| **Pharmacist** | Dispense prescriptions, manage inventory | `/pharmacist/*` |

---

## 🔄 Complete System Flow (Simplified)

```
1. Patient books appointment → Status: PENDING
   ↓
2. Receptionist approves → Status: APPROVED (notifies doctor & patient)
   ↓
3. Doctor conducts consultation → Marks appointment COMPLETED
   ↓
4. Doctor issues prescription → Status: PENDING (generates PDF)
   ↓
5. Pharmacist dispenses medicine → Status: DISPENSED (notifies patient)
   ↓
6. Patient picks up medicine → COMPLETE
```

---

## 🗂️ Database Models

### User
- Stores all users (5 roles)
- Password hashed with pbkdf2:sha256
- `is_active` flag for account status

### Appointment
- Links patient + doctor
- Status: Pending → Approved/Rejected → Completed
- Stores date, time, notes

### Prescription
- Links to appointment, doctor, patient
- Contains diagnosis, medicine details (JSON)
- Status: Pending → Dispensed

### Medicine
- Inventory management
- Tracks quantity, expiry date
- Low stock alert at quantity < 50

### Notification
- User notifications system
- `is_read` flag for tracking

---

## 🔐 Authentication Flow

```
Login → Verify credentials → Create JWT token → Store in httpOnly cookie
         ↓
Protected route → Verify JWT → Extract user_id → Load user → Check role → Allow/Deny
```

**Token Lifetime**: 8 hours  
**Storage**: httpOnly cookie (XSS protection)

---

## 📁 Project Structure

```
app.py                  # Main application & routes
auth.py                 # Authentication decorators
config.py              # Configuration
models.py              # Database models

routes/
├── admin.py           # Admin routes
├── doctor.py          # Doctor routes
├── patient.py         # Patient routes
├── receptionist.py    # Receptionist routes
└── pharmacist.py      # Pharmacist routes

services/
├── chatbot_service.py # Medical AI chatbot
└── pdf_service.py     # PDF prescription generator

templates/             # HTML templates (Jinja2)
static/               # CSS, JS, PDF files
database/             # SQLite database
```

---

## 🛣️ Key Endpoints

### Authentication
- `POST /login` - User login
- `GET /logout` - User logout

### Patient Routes
- `GET /patient/dashboard` - Dashboard
- `GET /patient/book_appointment` - Booking form
- `POST /patient/book_appointment` - Submit booking
- `GET /patient/appointments` - View all appointments
- `GET /patient/prescriptions` - View all prescriptions
- `GET /patient/chatbot` - Chatbot interface
- `POST /api/chatbot` - Chatbot API

### Doctor Routes
- `GET /doctor/dashboard` - Dashboard
- `GET /doctor/appointments` - View appointments
- `GET /doctor/patient_history/<id>` - Patient history
- `GET /doctor/issue_prescription/<id>` - Prescription form
- `POST /doctor/issue_prescription/<id>` - Submit prescription

### Receptionist Routes
- `GET /receptionist/dashboard` - Dashboard
- `POST /receptionist/approve_appointment/<id>` - Approve
- `POST /receptionist/reject_appointment/<id>` - Reject

### Pharmacist Routes
- `GET /pharmacist/dashboard` - Dashboard
- `GET /pharmacist/prescriptions` - View prescriptions
- `POST /pharmacist/dispense_prescription/<id>` - Dispense
- `GET /pharmacist/inventory` - Medicine inventory
- `POST /pharmacist/add_medicine` - Add medicine
- `POST /pharmacist/update_medicine/<id>` - Update stock

### Admin Routes
- `GET /admin/dashboard` - Dashboard
- `GET /admin/users` - User management
- `POST /admin/add_user` - Add user
- `POST /admin/update_user/<id>` - Update user
- `POST /admin/toggle_user/<id>` - Toggle active status
- `POST /admin/delete_user/<id>` - Delete user

---

## 🎯 Common Workflows

### 🏥 Patient Books Appointment
```python
# 1. Patient selects doctor, date, time
# 2. System creates appointment (status='Pending')
appointment = Appointment(
    patient_id=current_user.id,
    doctor_id=selected_doctor_id,
    date=selected_date,
    time=selected_time,
    status='Pending',
    notes=symptom_notes
)

# 3. Notify all receptionists
for receptionist in receptionists:
    notification = Notification(
        receiver_id=receptionist.id,
        message=f"New appointment request from {patient.username}"
    )
    
# 4. Save and redirect
```

### 👨‍⚕️ Doctor Issues Prescription
```python
# 1. Doctor fills prescription form
prescription = Prescription(
    appointment_id=appointment.id,
    doctor_id=current_user.id,
    patient_id=appointment.patient_id,
    diagnosis="Patient diagnosis here",
    medicine_details='[{"name":"Medicine", "dosage":"100mg", "duration":"7 days"}]',
    issued_status='Pending'
)

# 2. Generate PDF
pdf_filename = generate_prescription_pdf(prescription)

# 3. Update appointment to Completed
appointment.status = 'Completed'

# 4. Notify patient and pharmacist
```

### 💊 Pharmacist Dispenses Medicine
```python
# 1. View prescription details
prescription = Prescription.query.get(prescription_id)

# 2. Verify patient (manually)
# 3. Check medicine availability
# 4. Update status
prescription.issued_status = 'Dispensed'

# 5. Notify patient
notification = Notification(
    receiver_id=prescription.patient_id,
    message="Your prescription is ready for pickup"
)
```

---

## 🧪 Testing Scenarios

### Scenario 1: Complete Patient Journey
1. Login as `patient1 / patient123`
2. Book appointment with doctor1
3. Logout
4. Login as `receptionist1 / receptionist123`
5. Approve the appointment
6. Logout
7. Login as `doctor1 / doctor123`
8. View appointment, issue prescription
9. Logout
10. Login as `pharmacist1 / pharmacist123`
11. Dispense prescription
12. Logout
13. Login as `patient1 / patient123`
14. View dispensed prescription, download PDF

### Scenario 2: Admin User Management
1. Login as `admin / admin123`
2. Navigate to Users page
3. Add new user (any role)
4. Update user details
5. Toggle user active status
6. View system statistics

### Scenario 3: Chatbot Interaction
1. Login as `patient1 / patient123`
2. Navigate to Chatbot
3. Test queries:
   - "I have a fever"
   - "What is paracetamol used for?"
   - "I have chest pain" (emergency)
   - "What should I do for headache?"

---

## 🔧 Important Functions

### Authentication Decorators

```python
@role_required('patient')  # Requires specific role
def patient_dashboard():
    pass

@login_required  # Requires any authenticated user
def profile():
    pass
```

### Get Current User
```python
user = get_current_user()
if user:
    print(f"Current user: {user.username}, Role: {user.role}")
```

### Password Management
```python
# Set password (hashing)
user.set_password('plaintext_password')

# Check password
if user.check_password('plaintext_password'):
    print("Password correct")
```

### Create Notification
```python
notification = Notification(
    receiver_id=user.id,
    message="Your notification message here",
    is_read=False
)
db.session.add(notification)
db.session.commit()
```

---

## 📊 Database Queries

### Get Pending Appointments
```python
pending = Appointment.query.filter_by(status='Pending').all()
```

### Get Doctor's Today's Appointments
```python
from datetime import date
today = date.today()
appointments = Appointment.query.filter_by(
    doctor_id=doctor_id,
    date=today,
    status='Approved'
).order_by(Appointment.time).all()
```

### Get Low Stock Medicines
```python
low_stock = Medicine.query.filter(Medicine.quantity < 50).all()
```

### Get Expiring Medicines
```python
from datetime import timedelta
expiry_threshold = date.today() + timedelta(days=30)
expiring = Medicine.query.filter(
    Medicine.expiry_date <= expiry_threshold,
    Medicine.expiry_date >= date.today()
).all()
```

### Get User's Unread Notifications
```python
unread = Notification.query.filter_by(
    receiver_id=user.id,
    is_read=False
).order_by(Notification.created_at.desc()).all()
```

### Get Active Users by Role
```python
doctors = User.query.filter_by(
    role='doctor',
    is_active=True
).all()
```

---

## 🎨 Frontend Components

### Flash Messages
```python
flash('Success message', 'success')  # Green
flash('Error message', 'danger')     # Red
flash('Warning message', 'warning')  # Yellow
flash('Info message', 'info')        # Blue
```

### Template Variables (Available in all templates)
```python
user                 # Current user object
role_color          # User's role color (hex)
unread_count        # Unread notifications count
hospital_name       # Hospital name from config
```

### Base Template Structure
```html
{% extends 'layouts/base.html' %}

{% block title %}Page Title{% endblock %}

{% block content %}
    <!-- Your content here -->
{% endblock %}
```

---

## 🐛 Common Issues & Solutions

### Issue: "No module named 'flask_sqlalchemy'"
```powershell
pip install Flask-SQLAlchemy
```

### Issue: "No module named 'reportlab'"
```powershell
pip install reportlab
```

### Issue: Database not found
```powershell
# Ensure database directory exists
New-Item -ItemType Directory -Path "database" -Force

# Run app to create database
python app.py
```

### Issue: JWT token errors
```python
# Clear browser cookies or use incognito mode
# Token might be expired (8 hour limit)
```

### Issue: Permission denied errors
```python
# Check user is_active flag
user = User.query.get(user_id)
print(user.is_active)  # Should be True

# Check user role
print(user.role)  # Should match required role
```

---

## 📝 Code Snippets

### Add New Route (Example)
```python
# In routes/patient.py
@patient_bp.route('/new_feature')
@role_required('patient')
def new_feature():
    current_user = get_current_user()
    # Your logic here
    return render_template('patient/new_feature.html', user=current_user)
```

### Add New Database Model
```python
# In models.py
class NewModel(db.Model):
    __tablename__ = 'new_models'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
```

### Add New Service
```python
# In services/new_service.py
def new_service_function(parameter):
    """
    Service description
    """
    # Your logic here
    return result
```

---

## 🔒 Security Best Practices

### ✅ DO:
- Always use `@role_required()` or `@login_required` decorators
- Hash passwords with `user.set_password()`
- Validate all user inputs
- Use SQLAlchemy queries (prevents SQL injection)
- Check `is_active` status before granting access
- Use httpOnly cookies for tokens

### ❌ DON'T:
- Store plain text passwords
- Trust user input without validation
- Use raw SQL queries
- Expose sensitive data in URLs
- Allow access without role checking
- Store JWT in localStorage (use httpOnly cookies)

---

## 📦 Dependencies

```txt
Flask==3.0.0
Flask-SQLAlchemy==3.1.1
Flask-JWT-Extended==4.6.0
reportlab==4.0.7
python-dateutil==2.8.2
Werkzeug==3.0.1
```

Install all:
```powershell
pip install -r requirements.txt
```

---

## 🚀 Deployment Checklist

- [ ] Change SECRET_KEY and JWT_SECRET_KEY
- [ ] Set JWT_COOKIE_SECURE = True (HTTPS)
- [ ] Enable CSRF protection
- [ ] Use PostgreSQL/MySQL instead of SQLite
- [ ] Set up proper logging
- [ ] Configure environment variables
- [ ] Use production WSGI server (Gunicorn/Waitress)
- [ ] Set up reverse proxy (Nginx)
- [ ] Enable database backups
- [ ] Configure CORS properly
- [ ] Set up monitoring
- [ ] Enable rate limiting

---

## 📞 API Response Formats

### Success Response
```json
{
    "success": true,
    "message": "Operation successful",
    "data": {...}
}
```

### Error Response
```json
{
    "success": false,
    "error": "Error message",
    "details": "Detailed error information"
}
```

### Chatbot Response
```json
{
    "response": "Chatbot response text with advice"
}
```

---

## 🎯 Performance Tips

1. **Database Queries**
   - Use `.all()` only when needed
   - Use `.limit()` for large result sets
   - Add indexes on frequently queried columns

2. **Templates**
   - Minimize database queries in templates
   - Pass pre-computed data from routes
   - Use template inheritance

3. **Static Files**
   - Minify CSS and JavaScript
   - Use CDN for libraries
   - Compress images

4. **Caching**
   - Cache static data (medicine list, doctor list)
   - Use Flask-Caching for expensive queries

---

## 📚 Resources

- **Flask Documentation**: https://flask.palletsprojects.com/
- **SQLAlchemy Docs**: https://docs.sqlalchemy.org/
- **JWT Extended**: https://flask-jwt-extended.readthedocs.io/
- **ReportLab Guide**: https://www.reportlab.com/docs/reportlab-userguide.pdf

---

## 🆘 Need Help?

### Check These First:
1. Console/terminal output for error messages
2. Browser developer console (F12) for frontend errors
3. Database file exists in `database/hospital.db`
4. All dependencies installed
5. Virtual environment activated

### Debug Mode:
```python
# In config.py or app.py
app.config['DEBUG'] = True  # Shows detailed errors
```

---

**Quick Reference Version**: 1.0  
**Last Updated**: February 17, 2026  
**For Full Documentation**: See SYSTEM_FLOW_DOCUMENTATION.md
