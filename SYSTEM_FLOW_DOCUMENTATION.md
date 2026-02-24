# Hospital Management System - Complete System Flow Documentation

## Table of Contents
1. [System Overview](#system-overview)
2. [System Architecture](#system-architecture)
3. [User Roles & Permissions](#user-roles--permissions)
4. [Authentication Flow](#authentication-flow)
5. [Database Models & Relationships](#database-models--relationships)
6. [Detailed User Flows](#detailed-user-flows)
7. [API Endpoints Reference](#api-endpoints-reference)
8. [Services Architecture](#services-architecture)
9. [System Flow Diagrams](#system-flow-diagrams)

---

## System Overview

The Hospital Management System is a comprehensive web-based application built with Flask that manages the complete workflow of a hospital, from patient registration and appointment booking to prescription management and pharmacy operations.

### Key Components
- **Frontend**: HTML templates with Bootstrap CSS, JavaScript
- **Backend**: Flask (Python web framework)
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: JWT (JSON Web Tokens) stored in cookies
- **File Storage**: Local file system for prescription PDFs
- **Services**: Chatbot Service, PDF Generation Service

### Technologies Used
- **Flask** - Web framework
- **Flask-SQLAlchemy** - Database ORM
- **Flask-JWT-Extended** - JWT authentication
- **ReportLab** - PDF generation
- **Werkzeug** - Password hashing
- **SQLite** - Database

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     CLIENT BROWSER                          │
│                  (HTML/CSS/JavaScript)                      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ HTTP Requests
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   FLASK APPLICATION                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              app.py (Main Entry)                      │  │
│  └──────────────────────────────────────────────────────┘  │
│                         │                                   │
│  ┌──────────────────────┼────────────────────────────────┐ │
│  │    Authentication    │         Routes                 │ │
│  │    (auth.py)         │    (Blueprints)                │ │
│  │  - JWT Verification  │    - admin.py                  │ │
│  │  - Role Checking     │    - doctor.py                 │ │
│  │  - Login Required    │    - patient.py                │ │
│  └──────────────────────┤    - receptionist.py           │ │
│                         │    - pharmacist.py             │ │
│                         └────────────────────────────────┘ │
│                         │                                   │
│  ┌──────────────────────┼────────────────────────────────┐ │
│  │      Services        │      Models                     │ │
│  │  - chatbot_service   │    (models.py)                 │ │
│  │  - pdf_service       │    - User                      │ │
│  └──────────────────────┤    - Appointment              │ │
│                         │    - Prescription             │ │
│                         │    - Medicine                 │ │
│                         │    - Notification             │ │
│                         └────────────────────────────────┘ │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              DATABASE (SQLite)                              │
│                 hospital.db                                 │
└─────────────────────────────────────────────────────────────┘
```

---

## User Roles & Permissions

### 1. **ADMIN**
**Primary Responsibilities:**
- Complete system control and oversight
- User management across all roles
- System configuration and monitoring
- View all data and analytics

**Key Permissions:**
✅ Create, update, delete users
✅ View all appointments, prescriptions, medicines
✅ Access system-wide statistics
✅ Manage user activation/deactivation
✅ Reset passwords
✅ View audit trails

**Access Routes:**
- `/admin/dashboard`
- `/admin/users`
- `/admin/appointments`
- `/admin/prescriptions`

---

### 2. **DOCTOR**
**Primary Responsibilities:**
- View and manage approved appointments
- Issue prescriptions to patients
- Access patient medical history
- Receive appointment notifications

**Key Permissions:**
✅ View own appointments
✅ Issue and manage prescriptions
✅ View patient history (for own patients)
✅ Complete appointments
✅ Download prescription PDFs

**Access Routes:**
- `/doctor/dashboard`
- `/doctor/appointments`
- `/doctor/patient_history/<patient_id>`
- `/doctor/issue_prescription/<appointment_id>`
- `/doctor/prescriptions`
- `/doctor/notifications`

---

### 3. **PATIENT**
**Primary Responsibilities:**
- Book appointments with doctors
- View appointment status
- Access prescriptions
- Use medical chatbot for queries
- Receive notifications

**Key Permissions:**
✅ Book new appointments
✅ View own appointments
✅ View own prescriptions
✅ Download prescription PDFs
✅ Use AI chatbot
✅ View profile and analytics

**Access Routes:**
- `/patient/dashboard`
- `/patient/book_appointment`
- `/patient/appointments`
- `/patient/prescriptions`
- `/patient/chatbot`
- `/patient/notifications`
- `/patient/profile`
- `/patient/analytics`

---

### 4. **RECEPTIONIST**
**Primary Responsibilities:**
- Manage patient appointment requests
- Approve or reject appointments
- Manage patient queue
- Coordinate doctor schedules

**Key Permissions:**
✅ View all appointments
✅ Approve/reject pending appointments
✅ Manage appointment queue
✅ Send notifications to patients/doctors

**Access Routes:**
- `/receptionist/dashboard`
- `/receptionist/appointments`
- `/receptionist/queue`

---

### 5. **PHARMACIST**
**Primary Responsibilities:**
- View and dispense prescriptions
- Manage medicine inventory
- Track stock levels and expiry dates
- Handle low stock alerts

**Key Permissions:**
✅ View all prescriptions
✅ Mark prescriptions as dispensed
✅ Manage medicine inventory (add/update/delete)
✅ View low stock alerts
✅ Track expiry dates
✅ View dispensing history

**Access Routes:**
- `/pharmacist/dashboard`
- `/pharmacist/prescriptions`
- `/pharmacist/inventory`
- `/pharmacist/low_stock_alerts`
- `/pharmacist/expiry_tracking`
- `/pharmacist/dispensing_history`

---

## Authentication Flow

```mermaid
sequenceDiagram
    participant User
    participant Browser
    participant Flask
    participant JWT
    participant Database

    User->>Browser: Enter credentials
    Browser->>Flask: POST /login
    Flask->>Database: Query User by username
    Database-->>Flask: Return User object
    Flask->>Flask: Verify password (check_password)
    Flask->>Flask: Check is_active status
    Flask->>JWT: Create access token
    JWT-->>Flask: Return JWT token
    Flask->>Browser: Set JWT cookie + Redirect
    Browser->>Browser: Store JWT in httpOnly cookie
    Browser->>Flask: GET /{role}_dashboard
    Flask->>JWT: Verify JWT from cookie
    JWT-->>Flask: Extract user_id
    Flask->>Database: Get User by id
    Database-->>Flask: Return User
    Flask->>Flask: Check role permissions
    Flask-->>Browser: Render dashboard
    Browser-->>User: Display dashboard
```

### Authentication Process Steps:

1. **Login (POST /login)**
   - User submits username and password
   - System validates credentials against database
   - Password is hashed using Werkzeug's pbkdf2:sha256
   - If valid, JWT token is created with user.id as identity
   - Token is stored in httpOnly cookie (XSS protection)
   - User is redirected to role-specific dashboard

2. **Route Protection**
   - Each protected route uses decorators:
     - `@login_required` - Requires any authenticated user
     - `@role_required('role_name')` - Requires specific role
   - JWT is extracted from cookie and verified
   - User object is loaded from database
   - Role permissions are checked
   - Inactive users are automatically logged out

3. **Session Management**
   - JWT expires after 8 hours (configurable)
   - Logout clears JWT cookie
   - Token refresh not implemented (user must re-login)

4. **Security Features**
   - Passwords hashed with pbkdf2:sha256
   - JWT stored in httpOnly cookies
   - CSRF protection disabled (development mode)
   - Role-based access control (RBAC)
   - Account deactivation capability

---

## Database Models & Relationships

### Entity Relationship Diagram

```
┌─────────────────────┐
│       USER          │
│─────────────────────│
│ id (PK)             │
│ username (unique)   │◄───────────────┐
│ email (unique)      │                │
│ password_hash       │                │
│ role                │                │
│ is_active           │                │
│ created_at          │                │
└──────┬──────────────┘                │
       │                               │
       │ 1:N (as patient)              │
       │                               │
       ▼                               │
┌─────────────────────┐                │
│   APPOINTMENT       │                │
│─────────────────────│                │
│ id (PK)             │                │
│ patient_id (FK) ────┼────────────────┘
│ doctor_id (FK) ─────┼────────────────┐
│ date                │                │
│ time                │                │
│ status              │                │
│ notes               │                │
│ created_at          │                │
└──────┬──────────────┘                │
       │                               │
       │ 1:N                           │
       │                               │
       ▼                               │
┌─────────────────────┐                │
│   PRESCRIPTION      │                │
│─────────────────────│                │
│ id (PK)             │                │
│ appointment_id (FK) │                │
│ doctor_id (FK) ─────┼────────────────┘
│ patient_id (FK) ────┼────────────────┐
│ diagnosis           │                │
│ medicine_details    │                │
│ issued_status       │                │
│ created_at          │                │
└─────────────────────┘                │
                                       │
┌─────────────────────┐                │
│    MEDICINE         │                │
│─────────────────────│                │
│ id (PK)             │                │
│ name (unique)       │                │
│ quantity            │                │
│ expiry_date         │                │
│ created_at          │                │
└─────────────────────┘                │
                                       │
┌─────────────────────┐                │
│   NOTIFICATION      │                │
│─────────────────────│                │
│ id (PK)             │                │
│ receiver_id (FK) ───┼────────────────┘
│ message             │
│ is_read             │
│ created_at          │
└─────────────────────┘
```

### Model Descriptions

#### 1. **User Model**
```python
Attributes:
- id: Primary key
- username: Unique identifier for login
- email: User's email address (unique)
- password_hash: Hashed password (pbkdf2:sha256)
- role: One of ['admin', 'doctor', 'patient', 'receptionist', 'pharmacist']
- is_active: Boolean flag for account status
- created_at: Registration timestamp

Relationships:
- appointments_as_patient: Appointments where user is patient (1:N)
- appointments_as_doctor: Appointments where user is doctor (1:N)
- prescriptions_as_patient: Prescriptions for user as patient (1:N)
- prescriptions_as_doctor: Prescriptions issued by user as doctor (1:N)
- notifications: Notifications received by user (1:N, cascade delete)

Methods:
- set_password(password): Hash and store password
- check_password(password): Verify password
- to_dict(): Convert to dictionary
```

#### 2. **Appointment Model**
```python
Attributes:
- id: Primary key
- patient_id: Foreign key to User (patient)
- doctor_id: Foreign key to User (doctor)
- date: Appointment date
- time: Appointment time
- status: ['Pending', 'Approved', 'Rejected', 'Completed']
- notes: Additional notes/symptoms
- created_at: Booking timestamp

Relationships:
- patient: User object (patient)
- doctor: User object (doctor)
- prescriptions: Related prescriptions (1:N)

Methods:
- to_dict(): Convert to dictionary
```

#### 3. **Prescription Model**
```python
Attributes:
- id: Primary key
- appointment_id: Foreign key to Appointment
- doctor_id: Foreign key to User (doctor)
- patient_id: Foreign key to User (patient)
- diagnosis: Medical diagnosis text
- medicine_details: JSON string with medicine list
- issued_status: ['Pending', 'Dispensed']
- created_at: Issuance timestamp

Relationships:
- appointment: Related appointment
- doctor: Prescribing doctor
- patient: Patient

Methods:
- to_dict(): Convert to dictionary
```

#### 4. **Medicine Model**
```python
Attributes:
- id: Primary key
- name: Medicine name (unique)
- quantity: Stock quantity
- expiry_date: Expiration date
- created_at: Creation timestamp

Methods:
- is_low_stock(threshold=50): Check if stock is low
- is_expired(): Check if expired
- to_dict(): Convert to dictionary
```

#### 5. **Notification Model**
```python
Attributes:
- id: Primary key
- receiver_id: Foreign key to User
- message: Notification message text
- is_read: Boolean read status
- created_at: Creation timestamp

Relationships:
- receiver: User receiving notification

Methods:
- to_dict(): Convert to dictionary
```

---

## Detailed User Flows

### 🔷 PATIENT FLOW

#### 1. Patient Books Appointment
```
1. Patient logs in → Redirected to /patient/dashboard
2. Clicks "Book Appointment" → /patient/book_appointment
3. Selects:
   - Doctor from dropdown (active doctors only)
   - Date (must be present or future)
   - Time slot
   - Symptom notes (optional)
4. Submits form → POST /patient/book_appointment
5. System:
   - Validates doctor exists and is active
   - Validates date is not in the past
   - Creates Appointment with status='Pending'
   - Sends notification to all receptionists
   - Saves to database
6. Patient receives confirmation
7. Redirected to appointments page
```

#### 2. Patient Views Appointment Status
```
1. Navigate to /patient/appointments
2. System displays:
   - All appointments with status badges
   - Color coding: 
     * Pending (yellow)
     * Approved (green)
     * Rejected (red)
     * Completed (blue)
3. Can view appointment details:
   - Doctor name
   - Date and time
   - Status
   - Notes
```

#### 3. Patient Views Prescriptions
```
1. Navigate to /patient/prescriptions
2. System displays:
   - All prescriptions issued to patient
   - Doctor name, date, diagnosis
   - Medicine details
   - Dispensing status (Pending/Dispensed)
3. Patient can:
   - Download prescription as PDF
   - View medicine details
```

#### 4. Patient Uses Chatbot
```
1. Navigate to /patient/chatbot
2. Enter medical query (symptoms, medicine info)
3. POST /api/chatbot → chatbot_service.py
4. Chatbot analyzes:
   - Symptom keywords
   - Medicine information requests
   - Emergency keywords
5. Returns:
   - Possible conditions
   - General advice
   - Medicine information
   - Emergency alerts
6. Response displayed in chat interface
```

---

### 🔷 RECEPTIONIST FLOW

#### 1. View Pending Appointments
```
1. Login → /receptionist/dashboard
2. Dashboard shows:
   - All pending appointments (status='Pending')
   - Today's appointments
   - Statistics (total pending, approved, today)
3. Appointments sorted by date and time
```

#### 2. Approve Appointment
```
1. View appointment in dashboard/appointments list
2. Click "Approve" button
3. POST /receptionist/approve_appointment/<id>
4. System:
   - Validates appointment is Pending
   - Changes status to 'Approved'
   - Creates notification for patient (approval confirmation)
   - Creates notification for doctor (new appointment alert)
   - Saves to database
5. Success message displayed
6. Appointment moves to approved list
```

#### 3. Reject Appointment
```
1. Click "Reject" button on pending appointment
2. POST /receptionist/reject_appointment/<id>
3. System:
   - Validates appointment is Pending
   - Changes status to 'Rejected'
   - Creates notification for patient (rejection notice)
   - Saves to database
4. Rejection message displayed
```

#### 4. Manage Queue
```
1. Navigate to /receptionist/queue
2. View today's approved appointments
3. Displays:
   - Patient name
   - Doctor name
   - Appointment time
   - Status
4. Can complete appointments after consultation
```

---

### 🔷 DOCTOR FLOW

#### 1. View Appointments
```
1. Login → /doctor/dashboard
2. Dashboard shows:
   - Today's approved appointments
   - Recent approved appointments (last 20)
   - Prescription statistics
   - Unread notifications
3. All appointments sorted by date/time
```

#### 2. Issue Prescription
```
1. View appointment details
2. Click "Issue Prescription"
3. GET /doctor/issue_prescription/<appointment_id>
4. Form displays:
   - Patient information
   - Appointment details
   - Fields: Diagnosis, Medicines (JSON format)
5. Doctor fills:
   - Diagnosis text
   - Medicine details (name, dosage, duration, instructions)
6. Submit → POST /doctor/issue_prescription/<appointment_id>
7. System:
   - Validates appointment belongs to doctor
   - Creates Prescription record
   - Sets issued_status='Pending'
   - Generates PDF using pdf_service
   - Sends notification to patient
   - Sends notification to pharmacist
   - Marks appointment as 'Completed'
8. Redirects to prescriptions page
```

#### 3. View Patient History
```
1. Click patient name from appointment
2. GET /doctor/patient_history/<patient_id>
3. System displays:
   - Patient information
   - All previous appointments with this doctor
   - All prescriptions issued to patient by this doctor
   - Sorted by date (most recent first)
4. Can view detailed prescription information
```

#### 4. View Prescriptions
```
1. Navigate to /doctor/prescriptions
2. System shows:
   - All prescriptions issued by doctor
   - Patient names
   - Diagnosis
   - Issue date
   - Dispensing status
3. Can download PDFs
```

---

### 🔷 PHARMACIST FLOW

#### 1. View Pending Prescriptions
```
1. Login → /pharmacist/dashboard
2. Dashboard shows:
   - Pending prescriptions (issued_status='Pending')
   - Low stock medicines (quantity < 50)
   - Medicines expiring soon (within 30 days)
   - Statistics
```

#### 2. Dispense Prescription
```
1. View prescription details
2. Verify patient identity (in real scenario)
3. Click "Dispense" button
4. POST /pharmacist/dispense_prescription/<id>
5. System:
   - Validates prescription is Pending
   - Changes issued_status to 'Dispensed'
   - Creates notification for patient (ready for pickup)
   - Updates timestamp
6. Prescription moved to dispensed list
```

#### 3. Manage Inventory
```
1. Navigate to /pharmacist/inventory
2. View all medicines with:
   - Name, quantity, expiry date
   - Low stock indicators
   - Expired indicators
3. Can add new medicine:
   - POST /pharmacist/add_medicine
   - Fields: name, quantity, expiry_date
4. Can update quantity:
   - POST /pharmacist/update_medicine/<id>
   - Increments/decrements quantity
5. Can delete medicine:
   - POST /pharmacist/delete_medicine/<id>
```

#### 4. Monitor Stock Alerts
```
1. Navigate to /pharmacist/low_stock_alerts
2. System shows:
   - Medicines with quantity < 50
   - Sorted by quantity (lowest first)
3. Visual indicators for urgency:
   - Red: quantity < 20
   - Yellow: quantity < 50
```

#### 5. Track Expiry Dates
```
1. Navigate to /pharmacist/expiry_tracking
2. System displays:
   - Medicines expiring within 90 days
   - Expired medicines (should be removed)
   - Grouped by urgency
3. Color coding:
   - Red: Expired
   - Orange: < 30 days
   - Yellow: 30-90 days
```

---

### 🔷 ADMIN FLOW

#### 1. View Dashboard
```
1. Login → /admin/dashboard
2. Dashboard shows:
   - Total patients (active)
   - Total doctors (active)
   - Total pharmacists (active)
   - Appointments today
   - Total prescriptions
   - Pending appointments
   - Recent appointments (last 10)
   - Recent prescriptions (last 10)
   - All users list
```

#### 2. User Management
```
1. Navigate to /admin/users
2. View all users with:
   - Username, email, role
   - Active status
   - Creation date
3. Can add new user:
   - POST /admin/add_user
   - Fields: username, email, password, role
   - Validates uniqueness
4. Can update user:
   - POST /admin/update_user/<id>
   - Can change email, role
   - Can reset password
5. Can toggle active status:
   - POST /admin/toggle_user/<id>
   - Activates/deactivates account
6. Can delete user:
   - POST /admin/delete_user/<id>
   - Cascades to related appointments, notifications
```

#### 3. View All Appointments
```
1. Navigate to /admin/appointments
2. View all appointments system-wide
3. Filter options:
   - By status
   - By date range
   - By doctor
   - By patient
4. Can view details and statistics
```

#### 4. View All Prescriptions
```
1. Navigate to /admin/prescriptions
2. View all prescriptions
3. Filter options:
   - By doctor
   - By patient
   - By status
   - By date range
```

#### 5. Database Backup
```
1. Navigate to /admin/backup_database
2. Click "Create Backup"
3. POST /admin/backup_database
4. System:
   - Creates copy of hospital.db
   - Saves with timestamp
   - In database/backups/ folder
5. Returns confirmation with file name
```

---

## API Endpoints Reference

### Authentication Endpoints

```
POST /login
- Body: username, password
- Returns: JWT cookie, redirect to dashboard
- Public endpoint

GET /logout
- Returns: Clears JWT cookie, redirect to login
- Public endpoint
```

### Patient Endpoints

```
GET /patient/dashboard
- Auth: Patient role required
- Returns: Dashboard with appointments, prescriptions, stats

GET /patient/book_appointment
- Auth: Patient role required
- Returns: Appointment booking form with doctor list

POST /patient/book_appointment
- Auth: Patient role required
- Body: doctor_id, date, time, notes
- Returns: Creates appointment, redirect

GET /patient/appointments
- Auth: Patient role required
- Returns: All patient's appointments

GET /patient/prescriptions
- Auth: Patient role required
- Returns: All patient's prescriptions

GET /patient/chatbot
- Auth: Patient role required
- Returns: Chatbot interface

POST /api/chatbot
- Auth: Patient role required
- Body: message
- Returns: JSON {response: string}

GET /patient/notifications
- Auth: Patient role required
- Returns: All notifications

POST /patient/mark_notification_read/<id>
- Auth: Patient role required
- Returns: Marks notification as read

GET /patient/analytics
- Auth: Patient role required
- Returns: Patient health analytics

GET /patient/profile
- Auth: Patient role required
- Returns: Patient profile page

POST /patient/update_profile
- Auth: Patient role required
- Body: email, password (optional)
- Returns: Updates profile
```

### Doctor Endpoints

```
GET /doctor/dashboard
- Auth: Doctor role required
- Returns: Dashboard with appointments, stats

GET /doctor/appointments
- Auth: Doctor role required
- Returns: All doctor's approved appointments

GET /doctor/patient_history/<patient_id>
- Auth: Doctor role required
- Returns: Patient's history with this doctor

GET /doctor/issue_prescription/<appointment_id>
- Auth: Doctor role required
- Returns: Prescription form

POST /doctor/issue_prescription/<appointment_id>
- Auth: Doctor role required
- Body: diagnosis, medicine_details (JSON)
- Returns: Creates prescription, generates PDF

GET /doctor/prescriptions
- Auth: Doctor role required
- Returns: All prescriptions issued by doctor

GET /doctor/download_prescription/<id>
- Auth: Doctor role required
- Returns: PDF file download

GET /doctor/notifications
- Auth: Doctor role required
- Returns: All doctor notifications
```

### Receptionist Endpoints

```
GET /receptionist/dashboard
- Auth: Receptionist role required
- Returns: Dashboard with pending appointments

GET /receptionist/appointments
- Auth: Receptionist role required
- Returns: All appointments

POST /receptionist/approve_appointment/<id>
- Auth: Receptionist role required
- Returns: Approves appointment, sends notifications

POST /receptionist/reject_appointment/<id>
- Auth: Receptionist role required
- Returns: Rejects appointment, sends notification

GET /receptionist/queue
- Auth: Receptionist role required
- Returns: Today's appointment queue

POST /receptionist/complete_appointment/<id>
- Auth: Receptionist role required
- Returns: Marks appointment as completed
```

### Pharmacist Endpoints

```
GET /pharmacist/dashboard
- Auth: Pharmacist role required
- Returns: Dashboard with prescriptions, stock alerts

GET /pharmacist/prescriptions
- Auth: Pharmacist role required
- Returns: All prescriptions

POST /pharmacist/dispense_prescription/<id>
- Auth: Pharmacist role required
- Returns: Marks prescription as dispensed

GET /pharmacist/inventory
- Auth: Pharmacist role required
- Returns: All medicines in inventory

POST /pharmacist/add_medicine
- Auth: Pharmacist role required
- Body: name, quantity, expiry_date
- Returns: Creates new medicine

POST /pharmacist/update_medicine/<id>
- Auth: Pharmacist role required
- Body: quantity
- Returns: Updates medicine quantity

POST /pharmacist/delete_medicine/<id>
- Auth: Pharmacist role required
- Returns: Deletes medicine

GET /pharmacist/low_stock_alerts
- Auth: Pharmacist role required
- Returns: Low stock medicines

GET /pharmacist/expiry_tracking
- Auth: Pharmacist role required
- Returns: Medicines expiring soon

GET /pharmacist/dispensing_history
- Auth: Pharmacist role required
- Returns: Dispensed prescriptions history
```

### Admin Endpoints

```
GET /admin/dashboard
- Auth: Admin role required
- Returns: System-wide statistics and data

GET /admin/users
- Auth: Admin role required
- Returns: All users

POST /admin/add_user
- Auth: Admin role required
- Body: username, email, password, role
- Returns: Creates new user

POST /admin/update_user/<id>
- Auth: Admin role required
- Body: email, role, password (optional)
- Returns: Updates user

POST /admin/toggle_user/<id>
- Auth: Admin role required
- Returns: Toggles user active status

POST /admin/delete_user/<id>
- Auth: Admin role required
- Returns: Deletes user (cascade)

GET /admin/appointments
- Auth: Admin role required
- Returns: All appointments

GET /admin/prescriptions
- Auth: Admin role required
- Returns: All prescriptions

POST /admin/backup_database
- Auth: Admin role required
- Returns: Creates database backup
```

---

## Services Architecture

### 1. Chatbot Service (`services/chatbot_service.py`)

**Purpose**: Provides AI-like medical assistance to patients

**Features:**
- Symptom analysis
- Medicine information
- Emergency detection
- General health advice

**Knowledge Bases:**

```python
symptoms_db = {
    'fever': {conditions: [...], advice: '...'},
    'headache': {...},
    'cough': {...},
    'chest pain': {EMERGENCY},
    # ... more symptoms
}

medicine_db = {
    'paracetamol': {uses, dosage, side_effects},
    'ibuprofen': {...},
    # ... more medicines
}

emergency_keywords = [
    'chest pain', 'heart attack', 'stroke',
    'severe bleeding', 'unconscious', ...
]
```

**Processing Flow:**
```
1. Receive message from patient
2. Convert to lowercase, clean text
3. Check for emergency keywords → Emergency response
4. Check for medicine queries → Medicine info
5. Check for symptom keywords → Symptom advice
6. Default → General guidance
7. Return formatted response
```

**API Endpoint:**
```
POST /api/chatbot
Body: {message: "I have a headache"}
Response: {
    response: "Possible conditions: ...\nAdvice: ..."
}
```

---

### 2. PDF Service (`services/pdf_service.py`)

**Purpose**: Generate professional prescription PDFs

**Technology**: ReportLab library

**Features:**
- Hospital header with logo
- Doctor and patient information
- Prescription details
- Medicine list table
- Diagnosis information
- Signature section
- Footer with hospital info

**PDF Generation Flow:**
```
1. receive prescription object
2. Create PDFdocument (ReportLab)
3. Add hospital header (styled)
4. Add prescription metadata:
   - Prescription ID
   - Date issued
   - Patient name
   - Doctor name
5. Add diagnosis section
6. Create medicine table:
   - Medicine name
   - Dosage
   - Frequency
   - Duration
   - Instructions
7. Add doctor signature section
8. Add footer with hospital contact
9. Save to static/prescriptions/
10. Return filename
```

**File Naming:**
```
prescription_{id}_{YYYYMMDD_HHMMSS}.pdf
Example: prescription_42_20260217_143022.pdf
```

**Storage Location:**
```
static/prescriptions/prescription_*.pdf
```

---

## System Flow Diagrams

### Overall System Workflow

```mermaid
graph TB
    Start([User Access System]) --> Login[Login Page]
    Login --> Auth{Authenticate}
    Auth -->|Invalid| Login
    Auth -->|Valid| CheckRole{Check User Role}
    
    CheckRole -->|Admin| AdminDash[Admin Dashboard]
    CheckRole -->|Doctor| DoctorDash[Doctor Dashboard]
    CheckRole -->|Patient| PatientDash[Patient Dashboard]
    CheckRole -->|Receptionist| RecepDash[Receptionist Dashboard]
    CheckRole -->|Pharmacist| PharmDash[Pharmacist Dashboard]
    
    AdminDash --> AdminOps[User Management<br/>System Monitoring<br/>View All Data]
    
    PatientDash --> BookAppt[Book Appointment]
    BookAppt --> PendingAppt[Pending Status]
    PatientDash --> ViewRx[View Prescriptions]
    PatientDash --> Chatbot[Use Chatbot]
    
    RecepDash --> ViewPending[View Pending Appointments]
    ViewPending --> ApproveReject{Approve/Reject}
    ApproveReject -->|Approve| ApprovedAppt[Approved Status]
    ApproveReject -->|Reject| RejectedAppt[Rejected Status]
    
    ApprovedAppt --> DoctorDash
    DoctorDash --> ViewAppts[View Appointments]
    ViewAppts --> Consult[Consultation]
    Consult --> IssueRx[Issue Prescription]
    IssueRx --> RxPending[Prescription Pending]
    
    RxPending --> PharmDash
    PharmDash --> ViewRx2[View Prescriptions]
    ViewRx2 --> Dispense[Dispense Medicine]
    Dispense --> RxDispensed[Prescription Dispensed]
    PharmDash --> Inventory[Manage Inventory]
    
    RxDispensed --> PatientNotif[Notify Patient]
    PatientNotif --> ViewRx
```

### Appointment Lifecycle

```mermaid
stateDiagram-v2
    [*] --> Pending: Patient books appointment
    Pending --> Approved: Receptionist approves
    Pending --> Rejected: Receptionist rejects
    Approved --> Completed: Doctor completes consultation
    Completed --> [*]: Prescription issued
    Rejected --> [*]: Notification sent
```

### Prescription Lifecycle

```mermaid
stateDiagram-v2
    [*] --> Pending: Doctor issues prescription
    Pending --> Dispensed: Pharmacist dispenses medicine
    Dispensed --> [*]: Patient receives medicine
```

### User Authentication Flow

```mermaid
sequenceDiagram
    actor User
    participant Login Page
    participant Flask App
    participant JWT Service
    participant Database
    participant Dashboard

    User->>Login Page: Enter credentials
    Login Page->>Flask App: POST /login
    Flask App->>Database: Query user
    Database-->>Flask App: User data
    Flask App->>Flask App: Verify password
    Flask App->>Flask App: Check is_active
    Flask App->>JWT Service: Create token
    JWT Service-->>Flask App: JWT token
    Flask App->>Login Page: Set cookie + redirect
    Login Page->>Dashboard: Navigate to role dashboard
    Dashboard->>Flask App: Request with JWT cookie
    Flask App->>JWT Service: Verify token
    JWT Service-->>Flask App: User ID
    Flask App->>Database: Get user details
    Database-->>Flask App: User object
    Flask App->>Flask App: Check role permission
    Flask App-->>Dashboard: Render page
    Dashboard-->>User: Display dashboard
```

### Patient Appointment Booking Flow

```mermaid
sequenceDiagram
    actor Patient
    participant UI
    participant Flask
    participant DB
    participant Receptionist

    Patient->>UI: Click "Book Appointment"
    UI->>Flask: GET /patient/book_appointment
    Flask->>DB: Get active doctors
    DB-->>Flask: Doctor list
    Flask-->>UI: Render form with doctors
    UI-->>Patient: Show form
    Patient->>UI: Fill form (doctor, date, time)
    UI->>Flask: POST /patient/book_appointment
    Flask->>Flask: Validate input
    Flask->>DB: Create appointment (Pending)
    Flask->>DB: Create notification for receptionist
    DB-->>Flask: Success
    Flask-->>UI: Redirect to appointments
    UI-->>Patient: Show success message
    Flask->>Receptionist: Send notification
```

### Doctor Prescription Issuance Flow

```mermaid
sequenceDiagram
    actor Doctor
    participant UI
    participant Flask
    participant DB
    participant PDF Service
    participant Patient
    participant Pharmacist

    Doctor->>UI: View appointment
    UI->>Flask: GET /doctor/issue_prescription/42
    Flask->>DB: Get appointment details
    DB-->>Flask: Appointment data
    Flask-->>UI: Render prescription form
    UI-->>Doctor: Show form
    Doctor->>UI: Fill diagnosis & medicines
    UI->>Flask: POST prescription data
    Flask->>DB: Create prescription record
    Flask->>PDF Service: Generate PDF
    PDF Service-->>Flask: Save PDF file
    Flask->>DB: Update appointment to Completed
    Flask->>DB: Create notification for patient
    Flask->>DB: Create notification for pharmacist
    DB-->>Flask: Success
    Flask-->>UI: Redirect to prescriptions
    UI-->>Doctor: Show success
    Flask->>Patient: Send notification
    Flask->>Pharmacist: Send notification
```

### Pharmacist Dispensing Flow

```mermaid
sequenceDiagram
    actor Pharmacist
    participant UI
    participant Flask
    participant DB
    participant Patient

    Pharmacist->>UI: View pending prescriptions
    UI->>Flask: GET /pharmacist/prescriptions
    Flask->>DB: Get all prescriptions
    DB-->>Flask: Prescription list
    Flask-->>UI: Render list
    UI-->>Pharmacist: Show prescriptions
    Pharmacist->>UI: Click "Dispense"
    UI->>Flask: POST /pharmacist/dispense_prescription/42
    Flask->>DB: Get prescription
    DB-->>Flask: Prescription data
    Flask->>DB: Update status to Dispensed
    Flask->>DB: Create notification for patient
    DB-->>Flask: Success
    Flask-->>UI: Redirect with success message
    UI-->>Pharmacist: Show success
    Flask->>Patient: Send notification
```

### Admin User Management Flow

```mermaid
sequenceDiagram
    actor Admin
    participant UI
    participant Flask
    participant DB

    Admin->>UI: Navigate to Users page
    UI->>Flask: GET /admin/users
    Flask->>DB: Get all users
    DB-->>Flask: User list
    Flask-->>UI: Render users table
    UI-->>Admin: Show all users
    Admin->>UI: Click "Add User"
    UI-->>Admin: Show form
    Admin->>UI: Fill user details
    UI->>Flask: POST /admin/add_user
    Flask->>Flask: Validate input
    Flask->>DB: Check username/email unique
    DB-->>Flask: Validation result
    Flask->>Flask: Hash password
    Flask->>DB: Create new user
    DB-->>Flask: Success
    Flask-->>UI: Redirect with success
    UI-->>Admin: Show updated user list
```

---

## Data Flow Summary

### 1. **Appointment Workflow**
```
Patient → Book Appointment (Pending)
    ↓
Receptionist → Approve/Reject
    ↓ (if approved)
Doctor → View & Consult
    ↓
Doctor → Issue Prescription
    ↓
Pharmacist → Dispense Medicine
    ↓
Patient → Receive Medicine
```

### 2. **Prescription Workflow**
```
Appointment Completed
    ↓
Doctor → Create Prescription
    ↓
PDF Service → Generate PDF
    ↓
Notifications → Patient + Pharmacist
    ↓
Pharmacist → View Pending
    ↓
Pharmacist → Dispense
    ↓
Notification → Patient (Ready for pickup)
```

### 3. **Notification System**
```
Trigger Events:
- Appointment booked → Notify receptionist
- Appointment approved → Notify patient + doctor
- Appointment rejected → Notify patient
- Prescription issued → Notify patient + pharmacist
- Prescription dispensed → Notify patient

Flow:
Event → Create Notification in DB → User sees in dashboard
```

### 4. **Medicine Inventory Workflow**
```
Pharmacist → Add Medicine (name, qty, expiry)
    ↓
System → Monitor stock levels
    ↓
If qty < 50 → Low Stock Alert
    ↓
If expiry < 30 days → Expiry Alert
    ↓
Pharmacist → Reorder/Update
```

---

## Security Features

### 1. **Authentication Security**
- ✅ Password hashing (pbkdf2:sha256)
- ✅ JWT token-based authentication
- ✅ HttpOnly cookies (XSS protection)
- ✅ 8-hour token expiration
- ✅ Automatic logout on inactive accounts

### 2. **Authorization Security**
- ✅ Role-based access control (RBAC)
- ✅ Route-level permission checks
- ✅ Resource ownership validation
  - Doctors can only view their own appointments
  - Patients can only view their own data
- ✅ Admin-only user management

### 3. **Data Security**
- ✅ SQL injection prevention (SQLAlchemy ORM)
- ✅ Input validation on all forms
- ✅ Unique constraints on usernames/emails
- ✅ Active status checks
- ✅ Cascade deletes for data integrity

### 4. **Session Security**
- ✅ Secure session cookies
- ✅ SameSite cookie attribute
- ✅ Session timeout
- ✅ Token verification on each request

---

## Default Test Users

```
Admin:
Username: admin
Password: admin123
Access: Full system control

Doctor:
Username: doctor1
Password: doctor123
Access: View appointments, issue prescriptions

Patient:
Username: patient1
Password: patient123
Access: Book appointments, view prescriptions

Receptionist:
Username: receptionist1
Password: receptionist123
Access: Approve/reject appointments

Pharmacist:
Username: pharmacist1
Password: pharmacist123
Access: Dispense prescriptions, manage inventory
```

---

## Technology Stack Summary

| Layer | Technology |
|-------|-----------|
| **Frontend** | HTML5, CSS3 (Bootstrap 5), JavaScript |
| **Backend Framework** | Flask 3.x (Python) |
| **Database** | SQLite with SQLAlchemy ORM |
| **Authentication** | Flask-JWT-Extended |
| **Password Hashing** | Werkzeug Security (pbkdf2:sha256) |
| **PDF Generation** | ReportLab |
| **File Storage** | Local filesystem |
| **Web Server** | Flask development server / Waitress |
| **Python Version** | Python 3.8+ |

---

## File Structure

```
Project_hospital/
├── app.py                      # Main application entry point
├── auth.py                     # Authentication & authorization
├── config.py                   # Configuration settings
├── models.py                   # Database models
├── requirements.txt            # Python dependencies
├── database/
│   └── hospital.db            # SQLite database
├── routes/                     # Blueprint modules
│   ├── __init__.py
│   ├── admin.py               # Admin routes
│   ├── doctor.py              # Doctor routes
│   ├── patient.py             # Patient routes
│   ├── pharmacist.py          # Pharmacist routes
│   └── receptionist.py        # Receptionist routes
├── services/                   # Business logic services
│   ├── __init__.py
│   ├── chatbot_service.py     # Medical chatbot
│   └── pdf_service.py         # PDF generation
├── static/                     # Static assets
│   ├── css/
│   │   └── style.css          # Custom styles
│   ├── js/
│   │   └── script.js          # Custom JavaScript
│   └── prescriptions/         # Generated PDFs
└── templates/                  # HTML templates
    ├── login.html
    ├── 403.html, 404.html, 500.html
    ├── layouts/
    │   └── base.html          # Base template
    ├── admin/                 # Admin templates
    ├── doctor/                # Doctor templates
    ├── patient/               # Patient templates
    ├── pharmacist/            # Pharmacist templates
    └── receptionist/          # Receptionist templates
```

---

## Future Enhancements

1. **Real-time Features**
   - WebSocket integration for live notifications
   - Real-time appointment queue updates
   - Live chat support

2. **Advanced Features**
   - Email notifications (SMTP integration)
   - SMS alerts (Twilio integration)
   - Payment gateway for billing
   - Medical reports upload
   - Video consultation integration
   - Lab test management

3. **Security Enhancements**
   - Two-factor authentication (2FA)
   - CSRF protection in production
   - Rate limiting
   - Audit logging
   - Data encryption at rest

4. **Analytics**
   - Patient health trends
   - Doctor performance metrics
   - Pharmacy inventory forecasting
   - Appointment analytics

5. **Mobile App**
   - React Native mobile application
   - Push notifications
   - Offline mode support

---

## Deployment Considerations

### Production Setup:
1. Use PostgreSQL/MySQL instead of SQLite
2. Enable HTTPS (SSL/TLS)
3. Set JWT_COOKIE_SECURE = True
4. Enable CSRF protection
5. Use production WSGI server (Gunicorn, uWSGI)
6. Set up reverse proxy (Nginx)
7. Enable database backups
8. Set up monitoring (New Relic, DataDog)
9. Configure environment variables
10. Enable logging (rotate logs)

### Environment Variables:
```bash
SECRET_KEY=your-production-secret-key
JWT_SECRET_KEY=your-jwt-secret-key
DATABASE_URL=postgresql://user:pass@host:5432/dbname
FLASK_ENV=production
```

---

## Conclusion

This Hospital Management System provides a comprehensive solution for managing hospital operations across multiple user roles. The system follows best practices for security, scalability, and maintainability, with clear separation of concerns and modular architecture.

The role-based access control ensures proper authorization, while the notification system keeps all stakeholders informed. The chatbot service provides immediate medical guidance, and the PDF generation creates professional prescriptions.

The system is designed to be extensible, allowing for future enhancements while maintaining code quality and performance.

---

**Document Version**: 1.0  
**Last Updated**: February 17, 2026  
**Author**: GitHub Copilot  
**System Version**: 1.0.0
