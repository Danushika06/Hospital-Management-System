# Hospital Management System - Visual Flow Diagrams

## Complete System Flow Diagrams using Mermaid

This document contains detailed visual representations of all system flows and interactions in the Hospital Management System.

---

## 1. Complete System Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        Browser[Web Browser]
        UI[User Interface<br/>HTML/CSS/JS]
    end
    
    subgraph "Application Layer"
        Flask[Flask Application]
        Auth[Authentication<br/>JWT Service]
        Routes[Route Blueprints]
        Services[Business Services]
    end
    
    subgraph "Data Layer"
        SQLAlchemy[SQLAlchemy ORM]
        DB[(SQLite Database)]
        Files[File System<br/>PDF Storage]
    end
    
    Browser --> UI
    UI --> Flask
    Flask --> Auth
    Flask --> Routes
    Routes --> Services
    Services --> SQLAlchemy
    SQLAlchemy --> DB
    Services --> Files
    
    Auth -.-> DB
```

---

## 2. User Authentication & Authorization Flow

```mermaid
sequenceDiagram
    participant U as User
    participant B as Browser
    participant F as Flask App
    participant A as Auth Module
    participant J as JWT Service
    participant D as Database

    rect rgb(240, 248, 255)
        Note over U,D: Login Process
        U->>B: Enter credentials
        B->>F: POST /login
        F->>D: SELECT * FROM users WHERE username=?
        D-->>F: User record
        F->>A: check_password(input, hash)
        A-->>F: Password valid
        F->>A: Check is_active status
        A-->>F: User is active
        F->>J: create_access_token(user.id)
        J-->>F: JWT token
        F->>B: Set httpOnly cookie + redirect
        B->>B: Store JWT cookie
        B-->>U: Redirect to dashboard
    end

    rect rgb(240, 255, 240)
        Note over U,D: Accessing Protected Route
        U->>B: Navigate to protected page
        B->>F: GET /dashboard (with JWT cookie)
        F->>J: verify_jwt_in_request()
        J->>J: Decode JWT token
        J-->>F: user_id extracted
        F->>D: SELECT * FROM users WHERE id=?
        D-->>F: User object
        F->>A: Check role permissions
        A-->>F: Permission granted
        F-->>B: Render page with user data
        B-->>U: Display dashboard
    end

    rect rgb(255, 240, 240)
        Note over U,D: Logout Process
        U->>B: Click logout
        B->>F: GET /logout
        F->>B: Clear JWT cookie
        B->>B: Delete cookie
        B-->>U: Redirect to login
    end
```

---

## 3. Complete Patient Journey

```mermaid
graph TD
    Start([Patient Logs In]) --> Dashboard[Patient Dashboard]
    
    Dashboard --> Action{Choose Action}
    
    Action -->|Book Appointment| BookFlow[Book Appointment Flow]
    Action -->|View Appointments| ViewAppts[View Appointments]
    Action -->|View Prescriptions| ViewRx[View Prescriptions]
    Action -->|Use Chatbot| Chatbot[Medical Chatbot]
    Action -->|View Profile| Profile[Profile Page]
    
    BookFlow --> SelectDoctor[Select Doctor]
    SelectDoctor --> SelectDateTime[Select Date & Time]
    SelectDateTime --> AddNotes[Add Symptom Notes]
    AddNotes --> SubmitBooking[Submit Booking]
    SubmitBooking --> CreateAppt[Create Appointment<br/>Status: Pending]
    CreateAppt --> NotifyReceptionist[Notify Receptionist]
    NotifyReceptionist --> WaitApproval[Wait for Approval]
    
    WaitApproval --> RecepApproves{Receptionist<br/>Decision}
    RecepApproves -->|Approve| ApptApproved[Status: Approved<br/>Notify Patient]
    RecepApproves -->|Reject| ApptRejected[Status: Rejected<br/>Notify Patient]
    
    ApptApproved --> NotifyDoctor[Notify Doctor]
    NotifyDoctor --> DoctorConsult[Doctor Consultation]
    DoctorConsult --> IssueRx[Doctor Issues<br/>Prescription]
    IssueRx --> RxCreated[Prescription Created<br/>Status: Pending]
    RxCreated --> NotifyPatient[Notify Patient]
    RxCreated --> NotifyPharmacist[Notify Pharmacist]
    
    NotifyPharmacist --> PharmView[Pharmacist Views<br/>Prescription]
    PharmView --> DispenseMed[Dispense Medicine]
    DispenseMed --> RxDispensed[Status: Dispensed]
    RxDispensed --> NotifyPickup[Notify Patient<br/>Ready for Pickup]
    
    NotifyPickup --> PatientPickup[Patient Collects<br/>Medicine]
    PatientPickup --> End([Journey Complete])
    
    ApptRejected --> Dashboard
    
    ViewAppts --> ApptList[List All Appointments<br/>with Status]
    ViewRx --> RxList[List All Prescriptions<br/>Download PDFs]
    Chatbot --> AskQuestion[Ask Medical Question]
    AskQuestion --> GetResponse[Get AI Response]
    GetResponse --> Dashboard
    
    Profile --> UpdateProfile[Update Email/Password]
    UpdateProfile --> Dashboard
    
    style Start fill:#4ade80
    style End fill:#4ade80
    style ApptApproved fill:#60a5fa
    style ApptRejected fill:#f87171
    style RxDispensed fill:#a78bfa
```

---

## 4. Receptionist Appointment Management Flow

```mermaid
graph TB
    Start([Receptionist Login]) --> Dashboard[Receptionist Dashboard]
    
    Dashboard --> ViewPending[View Pending<br/>Appointments]
    ViewPending --> PendingList[Display List:<br/>Patient Name<br/>Doctor Name<br/>Date & Time<br/>Notes]
    
    PendingList --> SelectAppt{Select<br/>Appointment}
    
    SelectAppt --> ViewDetails[View Full Details]
    ViewDetails --> Decision{Make Decision}
    
    Decision -->|Approve| ApproveFlow[Approve Process]
    Decision -->|Reject| RejectFlow[Reject Process]
    
    ApproveFlow --> CheckDoctor[Check Doctor<br/>Availability]
    CheckDoctor --> UpdateStatus1[Update Status<br/>to 'Approved']
    UpdateStatus1 --> CreateNotif1[Create Notification<br/>for Patient]
    CreateNotif1 --> CreateNotif2[Create Notification<br/>for Doctor]
    CreateNotif2 --> SaveDB1[Save to Database]
    SaveDB1 --> Success1[Show Success Message]
    Success1 --> Dashboard
    
    RejectFlow --> UpdateStatus2[Update Status<br/>to 'Rejected']
    UpdateStatus2 --> CreateNotif3[Create Notification<br/>for Patient]
    CreateNotif3 --> SaveDB2[Save to Database]
    SaveDB2 --> Success2[Show Success Message]
    Success2 --> Dashboard
    
    Dashboard --> ViewQueue[View Today's Queue]
    ViewQueue --> QueueList[Display Today's<br/>Appointments]
    QueueList --> ManageQueue[Manage Queue<br/>Order]
    ManageQueue --> CompleteAppt[Mark as Completed<br/>After Consultation]
    CompleteAppt --> Dashboard
    
    Dashboard --> ViewAll[View All<br/>Appointments]
    ViewAll --> FilterOpts[Filter Options:<br/>By Status<br/>By Date<br/>By Doctor]
    FilterOpts --> Dashboard
    
    style ApproveFlow fill:#86efac
    style RejectFlow fill:#fca5a5
    style Success1 fill:#4ade80
    style Success2 fill:#fb923c
```

---

## 5. Doctor Workflow - Consultation & Prescription

```mermaid
sequenceDiagram
    participant D as Doctor
    participant UI as User Interface
    participant F as Flask Backend
    participant DB as Database
    participant PDF as PDF Service
    participant P as Patient
    participant Ph as Pharmacist

    rect rgb(240, 248, 255)
        Note over D,Ph: View Appointments
        D->>UI: Login & view dashboard
        UI->>F: GET /doctor/dashboard
        F->>DB: Query approved appointments<br/>WHERE doctor_id = ? AND status = 'Approved'
        DB-->>F: Appointment list
        F-->>UI: Render dashboard with appointments
        UI-->>D: Display today's appointments
    end

    rect rgb(255, 248, 220)
        Note over D,Ph: View Patient History
        D->>UI: Click patient name
        UI->>F: GET /doctor/patient_history/123
        F->>DB: Query patient appointments & prescriptions<br/>WHERE patient_id = 123 AND doctor_id = ?
        DB-->>F: Patient history data
        F-->>UI: Render history page
        UI-->>D: Display patient's medical history
    end

    rect rgb(240, 255, 240)
        Note over D,Ph: Issue Prescription
        D->>UI: Click "Issue Prescription"
        UI->>F: GET /doctor/issue_prescription/456
        F->>DB: Get appointment details
        DB-->>F: Appointment data
        F-->>UI: Render prescription form
        UI-->>D: Show form with patient info
        
        D->>UI: Fill diagnosis & medicines
        Note over D: Medicine details format:<br/>{name, dosage, duration, instructions}
        UI->>F: POST prescription data
        
        F->>DB: BEGIN TRANSACTION
        F->>DB: INSERT INTO prescriptions
        DB-->>F: prescription_id
        
        F->>PDF: generate_prescription_pdf(prescription)
        PDF->>PDF: Create PDF document
        PDF->>PDF: Add header & patient info
        PDF->>PDF: Add diagnosis
        PDF->>PDF: Create medicine table
        PDF->>PDF: Add footer & signature
        PDF-->>F: Save to static/prescriptions/<br/>Return filename
        
        F->>DB: UPDATE appointments<br/>SET status = 'Completed'
        F->>DB: INSERT notification for patient
        F->>DB: INSERT notification for pharmacist
        F->>DB: COMMIT TRANSACTION
        
        F-->>UI: Success message
        UI-->>D: "Prescription issued successfully"
        
        F->>P: Send notification<br/>"Prescription issued"
        F->>Ph: Send notification<br/>"New prescription pending"
    end
```

---

## 6. Pharmacist Medicine Dispensing Flow

```mermaid
stateDiagram-v2
    [*] --> Login: Pharmacist login
    Login --> Dashboard: View dashboard
    
    state Dashboard {
        [*] --> ViewPending
        ViewPending --> ViewInventory
        ViewInventory --> ViewAlerts
        ViewAlerts --> [*]
    }
    
    Dashboard --> PrescriptionManagement: Select prescriptions
    
    state PrescriptionManagement {
        [*] --> ListPrescriptions: View all prescriptions
        ListPrescriptions --> SelectPrescription: Click prescription
        SelectPrescription --> ViewDetails: View full details
        ViewDetails --> VerifyPatient: Verify patient identity
        VerifyPatient --> CheckStock: Check medicine availability
        
        CheckStock --> DispenseDecision: Stock available?
        DispenseDecision --> PrepareMedicine: Yes
        DispenseDecision --> OrderStock: No - insufficient stock
        
        PrepareMedicine --> UpdateStatus: Update to 'Dispensed'
        UpdateStatus --> NotifyPatient: Send notification
        NotifyPatient --> UpdateInventory: Decrease stock
        UpdateInventory --> [*]
        
        OrderStock --> [*]: Return to list
    }
    
    Dashboard --> InventoryManagement: Select inventory
    
    state InventoryManagement {
        [*] --> ViewAllMedicines
        ViewAllMedicines --> ManageChoice: Choose action
        
        ManageChoice --> AddMedicine: Add new
        ManageChoice --> UpdateMedicine: Update existing
        ManageChoice --> DeleteMedicine: Remove
        
        AddMedicine --> ValidateInput: Enter details
        ValidateInput --> CheckDuplicate: Check if exists
        CheckDuplicate --> SaveNew: Not exists
        CheckDuplicate --> ShowError: Already exists
        SaveNew --> [*]
        ShowError --> [*]
        
        UpdateMedicine --> UpdateQuantity: Change quantity
        UpdateQuantity --> SaveUpdates: Save changes
        SaveUpdates --> [*]
        
        DeleteMedicine --> ConfirmDelete: Confirm action
        ConfirmDelete --> RemoveFromDB: Delete record
        RemoveFromDB --> [*]
    }
    
    Dashboard --> AlertMonitoring: View alerts
    
    state AlertMonitoring {
        [*] --> CheckLowStock
        CheckLowStock --> LowStockList: Quantity < 50
        LowStockList --> TakeAction: Order more
        TakeAction --> [*]
        
        CheckLowStock --> CheckExpiry
        CheckExpiry --> ExpiryList: Expiry < 30 days
        ExpiryList --> TakeAction2: Remove expired
        TakeAction2 --> [*]
    }
    
    PrescriptionManagement --> Dashboard
    InventoryManagement --> Dashboard
    AlertMonitoring --> Dashboard
    Dashboard --> [*]: Logout
```

---

## 7. Admin User Management Flow

```mermaid
graph TD
    Start([Admin Login]) --> Dashboard[Admin Dashboard]
    
    Dashboard --> Stats[View Statistics:<br/>Total Patients<br/>Total Doctors<br/>Appointments Today<br/>Total Prescriptions]
    
    Dashboard --> UserMgmt[User Management]
    UserMgmt --> ViewUsers[View All Users]
    ViewUsers --> UserList[Display User List<br/>Username | Email | Role | Status]
    
    UserList --> Action{Select Action}
    
    Action -->|Add User| AddFlow[Add New User]
    Action -->|Update User| UpdateFlow[Update Existing User]
    Action -->|Toggle Status| ToggleFlow[Activate/Deactivate User]
    Action -->|Delete User| DeleteFlow[Delete User]
    
    AddFlow --> AddForm[Show Add User Form]
    AddForm --> FillDetails[Fill Details:<br/>Username<br/>Email<br/>Password<br/>Role]
    FillDetails --> ValidateAdd[Validate Input]
    ValidateAdd --> CheckUnique{Username/Email<br/>Unique?}
    CheckUnique -->|Yes| HashPassword[Hash Password<br/>pbkdf2:sha256]
    CheckUnique -->|No| ErrorUnique[Show Error:<br/>Already Exists]
    ErrorUnique --> AddForm
    HashPassword --> CreateUser[Create User Record]
    CreateUser --> SaveUser[Save to Database]
    SaveUser --> SuccessAdd[Show Success Message]
    SuccessAdd --> ViewUsers
    
    UpdateFlow --> SelectUser[Select User to Update]
    SelectUser --> UpdateForm[Show Update Form<br/>Pre-filled Data]
    UpdateForm --> ModifyFields[Modify:<br/>Email<br/>Role<br/>Password optional]
    ModifyFields --> ValidateUpdate[Validate Input]
    ValidateUpdate --> SaveUpdate[Update Database]
    SaveUpdate --> SuccessUpdate[Show Success Message]
    SuccessUpdate --> ViewUsers
    
    ToggleFlow --> SelectToggle[Select User]
    SelectToggle --> CheckStatus{Current<br/>Status?}
    CheckStatus -->|Active| Deactivate[Set is_active = False]
    CheckStatus -->|Inactive| Activate[Set is_active = True]
    Deactivate --> SaveToggle[Update Database]
    Activate --> SaveToggle
    SaveToggle --> SuccessToggle[Show Success Message]
    SuccessToggle --> ViewUsers
    
    DeleteFlow --> SelectDelete[Select User to Delete]
    SelectDelete --> ConfirmDelete{Confirm<br/>Deletion?}
    ConfirmDelete -->|Yes| CascadeDelete[Delete User<br/>Cascade to:<br/>- Appointments<br/>- Notifications]
    ConfirmDelete -->|No| ViewUsers
    CascadeDelete --> RemoveDB[Remove from Database]
    RemoveDB --> SuccessDelete[Show Success Message]
    SuccessDelete --> ViewUsers
    
    Dashboard --> ViewAppts[View All Appointments]
    ViewAppts --> ApptFilters[Filter by:<br/>Status<br/>Date Range<br/>Doctor<br/>Patient]
    ApptFilters --> ApptReport[Generate Report]
    ApptReport --> Dashboard
    
    Dashboard --> ViewPrescriptions[View All Prescriptions]
    ViewPrescriptions --> RxFilters[Filter by:<br/>Doctor<br/>Patient<br/>Status<br/>Date Range]
    RxFilters --> RxReport[Generate Report]
    RxReport --> Dashboard
    
    Dashboard --> BackupDB[Database Backup]
    BackupDB --> CreateBackup[Create Backup Copy]
    CreateBackup --> Timestamp[Add Timestamp]
    Timestamp --> SaveBackup[Save to<br/>database/backups/]
    SaveBackup --> ConfirmBackup[Confirm Backup Created]
    ConfirmBackup --> Dashboard
    
    style SuccessAdd fill:#4ade80
    style SuccessUpdate fill:#4ade80
    style SuccessToggle fill:#4ade80
    style SuccessDelete fill:#4ade80
    style ErrorUnique fill:#f87171
```

---

## 8. Patient Chatbot Interaction Flow

```mermaid
sequenceDiagram
    participant P as Patient
    participant UI as Chatbot UI
    participant F as Flask Backend
    participant CB as Chatbot Service
    participant DB as Knowledge Base

    P->>UI: Navigate to chatbot page
    UI->>F: GET /patient/chatbot
    F-->>UI: Render chatbot interface
    UI-->>P: Display chat window

    rect rgb(255, 248, 220)
        Note over P,DB: Query Processing
        P->>UI: Type message: "I have a fever"
        UI->>F: POST /api/chatbot {message: "I have a fever"}
        F->>CB: process_chatbot_message(message)
        
        CB->>CB: Normalize text (lowercase)
        CB->>CB: Check for emergency keywords
        
        alt Emergency Detected
            CB->>CB: Match "chest pain" or "severe"
            CB-->>F: Emergency response
            F-->>UI: {response: "⚠️ EMERGENCY: Call 911..."}
        else Symptom Query
            CB->>DB: Check symptoms_db["fever"]
            DB-->>CB: {conditions: [...], advice: "..."}
            CB->>CB: Format response
            CB-->>F: Return advice
            F-->>UI: {response: "Possible conditions: Cold, Flu..."}
        else Medicine Query
            CB->>DB: Check medicine_db["paracetamol"]
            DB-->>CB: {uses: "...", dosage: "...", side_effects: "..."}
            CB->>CB: Format medicine info
            CB-->>F: Return medicine info
            F-->>UI: {response: "Paracetamol uses:..."}
        else General Query
            CB->>CB: Default response
            CB-->>F: General health advice
            F-->>UI: {response: "Please book appointment..."}
        end
        
        UI->>UI: Append response to chat
        UI-->>P: Display response
    end

    rect rgb(240, 255, 240)
        Note over P,DB: Follow-up Question
        P->>UI: "What medicine should I take?"
        UI->>F: POST /api/chatbot
        F->>CB: process_chatbot_message(message)
        CB->>CB: Detect medicine query
        CB->>CB: Extract keywords
        CB->>DB: Lookup in medicine_db
        DB-->>CB: Medicine information
        CB-->>F: Formatted response with disclaimer
        F-->>UI: {response: "Consider paracetamol... *Consult doctor*"}
        UI-->>P: Display with disclaimer
    end

    P->>UI: Click "Book Appointment"
    UI->>F: Redirect to /patient/book_appointment
    F-->>UI: Render booking form
    UI-->>P: Display appointment form
```

---

## 9. Database Relationships & Data Flow

```mermaid
erDiagram
    USER ||--o{ APPOINTMENT : creates_as_patient
    USER ||--o{ APPOINTMENT : assigned_as_doctor
    USER ||--o{ PRESCRIPTION : receives_as_patient
    USER ||--o{ PRESCRIPTION : issues_as_doctor
    USER ||--o{ NOTIFICATION : receives
    APPOINTMENT ||--o{ PRESCRIPTION : generates
    
    USER {
        int id PK
        string username UK
        string email UK
        string password_hash
        string role
        boolean is_active
        datetime created_at
    }
    
    APPOINTMENT {
        int id PK
        int patient_id FK
        int doctor_id FK
        date date
        time time
        string status
        text notes
        datetime created_at
    }
    
    PRESCRIPTION {
        int id PK
        int appointment_id FK
        int doctor_id FK
        int patient_id FK
        text diagnosis
        text medicine_details
        string issued_status
        datetime created_at
    }
    
    MEDICINE {
        int id PK
        string name UK
        int quantity
        date expiry_date
        datetime created_at
    }
    
    NOTIFICATION {
        int id PK
        int receiver_id FK
        text message
        boolean is_read
        datetime created_at
    }
```

---

## 10. Prescription PDF Generation Flow

```mermaid
graph TD
    Start([Doctor Issues Prescription]) --> CreateRecord[Create Prescription Record<br/>in Database]
    CreateRecord --> CallPDF[Call PDF Service<br/>generate_prescription_pdf]
    
    CallPDF --> InitPDF[Initialize ReportLab<br/>SimpleDocTemplate]
    InitPDF --> SetupPage[Setup Page:<br/>Letter size<br/>Margins]
    
    SetupPage --> AddHeader[Add Header Section]
    AddHeader --> HospitalName[Hospital Name<br/>& Logo]
    HospitalName --> HospitalInfo[Hospital Address<br/>Phone Number]
    
    HospitalInfo --> AddTitle[Add Title:<br/>'PRESCRIPTION']
    AddTitle --> AddDivider1[Add Horizontal Line]
    
    AddDivider1 --> AddMetadata[Add Metadata Section]
    AddMetadata --> PrescriptionID[Prescription ID: #XXX]
    PrescriptionID --> IssuedDate[Issued Date]
    
    IssuedDate --> AddPatientInfo[Add Patient Information]
    AddPatientInfo --> PatientName[Patient Name]
    PatientName --> PatientID[Patient ID]
    
    PatientID --> AddDoctorInfo[Add Doctor Information]
    AddDoctorInfo --> DoctorName[Doctor Name]
    DoctorName --> DoctorID[Doctor ID]
    
    DoctorID --> AddDivider2[Add Horizontal Line]
    AddDivider2 --> AddDiagnosis[Add Diagnosis Section]
    AddDiagnosis --> DiagnosisText[Diagnosis:<br/>Patient's condition]
    
    DiagnosisText --> AddMedicineSection[Add Medicine Section]
    AddMedicineSection --> ParseJSON[Parse medicine_details JSON]
    ParseJSON --> CreateTable[Create Medicine Table]
    
    CreateTable --> TableHeaders[Table Headers:<br/>Medicine | Dosage | Frequency | Duration | Instructions]
    TableHeaders --> AddRows[Add Medicine Rows]
    AddRows --> StyleTable[Apply Table Styling:<br/>- Grid lines<br/>- Header background<br/>- Alternating rows]
    
    StyleTable --> AddSignature[Add Signature Section]
    AddSignature --> DoctorSignLine[Doctor's Signature: ___________]
    DoctorSignLine --> DateSignLine[Date: ___________]
    
    DateSignLine --> AddFooter[Add Footer]
    AddFooter --> FooterText[Hospital Contact<br/>Disclaimer Text]
    
    FooterText --> BuildPDF[Build PDF Document]
    BuildPDF --> SaveFile[Save to File:<br/>static/prescriptions/<br/>prescription_ID_timestamp.pdf]
    
    SaveFile --> Return[Return Filename]
    Return --> End([PDF Generated])
    
    style Start fill:#4ade80
    style End fill:#4ade80
    style CreateTable fill:#60a5fa
    style SaveFile fill:#a78bfa
```

---

## 11. Notification System Flow

```mermaid
graph TB
    subgraph Appointment Notifications
        ApptBooked[Appointment Booked] --> NotifyRecep1[Notify All Receptionists:<br/>'New appointment request']
        
        ApptApproved[Appointment Approved] --> NotifyPatient1[Notify Patient:<br/>'Appointment approved']
        ApptApproved --> NotifyDoctor1[Notify Doctor:<br/>'New appointment scheduled']
        
        ApptRejected[Appointment Rejected] --> NotifyPatient2[Notify Patient:<br/>'Appointment rejected']
        
        ApptCompleted[Appointment Completed] --> NotifyPatient3[Notify Patient:<br/>'Consultation complete']
    end
    
    subgraph Prescription Notifications
        RxIssued[Prescription Issued] --> NotifyPatient4[Notify Patient:<br/>'Prescription issued']
        RxIssued --> NotifyPharmacist1[Notify Pharmacist:<br/>'New prescription pending']
        
        RxDispensed[Prescription Dispensed] --> NotifyPatient5[Notify Patient:<br/>'Medicine ready for pickup']
    end
    
    subgraph Inventory Notifications
        LowStock[Stock Below 50] --> NotifyPharmacist2[Notify Pharmacist:<br/>'Low stock alert']
        
        ExpiryWarning[Expiry Within 30 Days] --> NotifyPharmacist3[Notify Pharmacist:<br/>'Expiry warning']
    end
    
    subgraph Notification Processing
        AllNotifs[All Notifications] --> CreateRecord[Create Notification Record<br/>in Database]
        CreateRecord --> SetReceiver[Set receiver_id]
        SetReceiver --> SetMessage[Set message text]
        SetMessage --> SetUnread[Set is_read = False]
        SetUnread --> SaveDB[Save to Database]
        SaveDB --> DisplayDashboard[Display in Dashboard]
        DisplayDashboard --> UserViews[User Views Notification]
        UserViews --> MarkRead[Mark as Read<br/>is_read = True]
    end
    
    NotifyRecep1 --> AllNotifs
    NotifyPatient1 --> AllNotifs
    NotifyDoctor1 --> AllNotifs
    NotifyPatient2 --> AllNotifs
    NotifyPatient3 --> AllNotifs
    NotifyPatient4 --> AllNotifs
    NotifyPharmacist1 --> AllNotifs
    NotifyPatient5 --> AllNotifs
    NotifyPharmacist2 --> AllNotifs
    NotifyPharmacist3 --> AllNotifs
    
    style ApptBooked fill:#bae6fd
    style RxIssued fill:#ddd6fe
    style LowStock fill:#fed7aa
    style AllNotifs fill:#fef08a
```

---

## 12. Medicine Inventory Management Flow

```mermaid
stateDiagram-v2
    [*] --> InitialState: System Start
    
    InitialState --> CheckInventory: Scheduled Check
    
    state CheckInventory {
        [*] --> ScanAllMedicines
        ScanAllMedicines --> CheckQuantity: For each medicine
        
        CheckQuantity --> LowStockDetected: quantity < 50
        CheckQuantity --> NormalStock: quantity >= 50
        
        NormalStock --> CheckExpiry
        
        state CheckExpiry {
            [*] --> GetExpiryDate
            GetExpiryDate --> CalculateDaysLeft
            CalculateDaysLeft --> ExpiryStatus
        }
        
        CheckExpiry --> Expired: expiry_date < today
        CheckExpiry --> ExpiresSoon: expiry_date < 30 days
        CheckExpiry --> ExpiryOK: expiry_date >= 30 days
        
        LowStockDetected --> CreateLowStockAlert
        Expired --> CreateExpiryAlert: Critical!
        ExpiresSoon --> CreateExpiryWarning
        ExpiryOK --> [*]
        
        CreateLowStockAlert --> NotifyPharmacist1
        CreateExpiryAlert --> NotifyPharmacist2
        CreateExpiryWarning --> NotifyPharmacist3
        
        NotifyPharmacist1 --> [*]
        NotifyPharmacist2 --> [*]
        NotifyPharmacist3 --> [*]
    }
    
    CheckInventory --> PharmacistAction: Alert received
    
    state PharmacistAction {
        [*] --> ViewAlerts
        ViewAlerts --> DecideAction
        
        DecideAction --> OrderMore: Low stock
        DecideAction --> RemoveExpired: Expired
        DecideAction --> MonitorClosely: Expiring soon
        
        OrderMore --> UpdateQuantity
        UpdateQuantity --> AddToInventory
        AddToInventory --> [*]
        
        RemoveExpired --> DeleteMedicine
        DeleteMedicine --> [*]
        
        MonitorClosely --> [*]
    }
    
    PharmacistAction --> CheckInventory: Continuous monitoring
    
    state DispensingFlow {
        [*] --> ReceivePrescription
        ReceivePrescription --> ParseMedicines
        ParseMedicines --> CheckAvailability
        
        CheckAvailability --> SufficientStock: Available
        CheckAvailability --> InsufficientStock: Not enough
        
        SufficientStock --> DeductQuantity
        DeductQuantity --> UpdateInventoryRecord
        UpdateInventoryRecord --> MarkDispensed
        MarkDispensed --> [*]
        
        InsufficientStock --> NotifyShortage
        NotifyShortage --> [*]
    }
    
    PharmacistAction --> DispensingFlow: Dispense prescription
    DispensingFlow --> CheckInventory: Update triggers check
```

---

## 13. Error Handling & Exception Flow

```mermaid
graph TD
    Request[HTTP Request] --> TryCatch{Try Block}
    
    TryCatch -->|Success| ProcessRoute[Process Route Logic]
    TryCatch -->|Exception| CatchError[Catch Exception]
    
    ProcessRoute --> ValidateInput{Validate Input}
    ValidateInput -->|Valid| DBOperation[Database Operation]
    ValidateInput -->|Invalid| ValidationError[Validation Error]
    
    ValidationError --> FlashMessage1[Flash Error Message]
    FlashMessage1 --> Redirect1[Redirect to Form]
    
    DBOperation --> DBTryCatch{DB Try Block}
    DBTryCatch -->|Success| Commit[Commit Transaction]
    DBTryCatch -->|Exception| DBError[Database Error]
    
    DBError --> Rollback[Rollback Transaction]
    Rollback --> FlashMessage2[Flash Error Message]
    FlashMessage2 --> Redirect2[Redirect to Previous Page]
    
    Commit --> Success[Success Response]
    Success --> FlashSuccess[Flash Success Message]
    FlashSuccess --> RedirectSuccess[Redirect to Dashboard]
    
    CatchError --> CheckErrorType{Error Type}
    
    CheckErrorType -->|401 Unauthorized| Error401[401 Handler]
    CheckErrorType -->|403 Forbidden| Error403[403 Handler]
    CheckErrorType -->|404 Not Found| Error404[404 Handler]
    CheckErrorType -->|500 Server Error| Error500[500 Handler]
    
    Error401 --> LoginRedirect[Redirect to Login]
    Error403 --> Show403[Render 403.html]
    Error404 --> Show404[Render 404.html]
    Error500 --> Show500[Render 500.html]
    
    LoginRedirect --> End([End])
    Show403 --> End
    Show404 --> End
    Show500 --> End
    RedirectSuccess --> End
    Redirect1 --> End
    Redirect2 --> End
    
    style Success fill:#4ade80
    style ValidationError fill:#fbbf24
    style DBError fill:#f87171
    style Error500 fill:#dc2626
```

---

## 14. Session Management & Security Flow

```mermaid
sequenceDiagram
    participant U as User
    participant B as Browser
    participant F as Flask
    participant J as JWT Service
    participant D as Database

    rect rgb(255, 240, 240)
        Note over U,D: Login & Token Creation
        U->>B: Submit login form
        B->>F: POST /login (username, password)
        F->>D: Query user
        D-->>F: User object
        F->>F: Verify password hash<br/>(pbkdf2:sha256)
        F->>F: Check is_active flag
        F->>J: create_access_token(user.id)
        J->>J: Encode JWT with secret key<br/>Expiry: 8 hours
        J-->>F: JWT token
        F->>B: Set httpOnly cookie<br/>SameSite: Lax<br/>Secure: False (dev)
        B->>B: Store cookie securely
    end

    rect rgb(240, 255, 240)
        Note over U,D: Request with Token
        U->>B: Click protected page
        B->>F: GET /dashboard<br/>(Cookie: JWT)
        F->>J: verify_jwt_in_request()
        J->>J: Decode JWT
        J->>J: Check expiration
        J->>J: Verify signature
        J-->>F: Extract user_id
        F->>D: Get user by id
        D-->>F: User object
        F->>F: Check is_active
        F->>F: Check role permission
        F-->>B: Render page
    end

    rect rgb(255, 255, 240)
        Note over U,D: Token Expiration
        U->>B: Request after 8 hours
        B->>F: GET /dashboard (expired JWT)
        F->>J: verify_jwt_in_request()
        J->>J: Decode JWT
        J->>J: Check expiration
        J-->>F: Token expired
        F-->>B: Redirect to login
        B->>B: Clear cookie
        B-->>U: Show login page
    end

    rect rgb(240, 240, 255)
        Note over U,D: Account Deactivation
        U->>B: Request with valid JWT
        B->>F: GET /dashboard
        F->>J: verify_jwt_in_request()
        J-->>F: Valid token, user_id
        F->>D: Get user
        D-->>F: User (is_active = False)
        F->>F: Check is_active
        F-->>B: Redirect to login<br/>"Account deactivated"
    end

    rect rgb(255, 240, 255)
        Note over U,D: Logout
        U->>B: Click logout
        B->>F: GET /logout
        F->>B: unset_jwt_cookies()
        B->>B: Delete cookie
        B-->>U: Redirect to login
    end
```

---

## 15. Complete Data Flow Summary

```mermaid
graph LR
    subgraph Input Layer
        A[Patient] --> B[Web Browser]
        C[Doctor] --> B
        D[Receptionist] --> B
        E[Pharmacist] --> B
        F[Admin] --> B
    end
    
    subgraph Presentation Layer
        B --> G[HTML Templates]
        G --> H[CSS Styles]
        H --> I[JavaScript]
    end
    
    subgraph Application Layer
        I --> J[Flask Routes]
        J --> K[Authentication]
        K --> L[Authorization]
        L --> M[Business Logic]
        M --> N[Validation]
    end
    
    subgraph Service Layer
        N --> O[Chatbot Service]
        N --> P[PDF Service]
        O --> Q[Knowledge Base]
        P --> R[ReportLab]
    end
    
    subgraph Data Layer
        N --> S[SQLAlchemy ORM]
        S --> T[Database Models]
        T --> U[(SQLite DB)]
    end
    
    subgraph Storage Layer
        P --> V[File System]
        V --> W[PDF Storage]
    end
    
    subgraph Output Layer
        M --> X[JSON Responses]
        M --> Y[HTML Rendering]
        M --> Z[Redirects]
        X --> G
        Y --> G
        Z --> G
    end
    
    style U fill:#7c3aed
    style W fill:#06b6d4
    style Q fill:#f59e0b
```

---

## Conclusion

These comprehensive flow diagrams provide a complete visual representation of the Hospital Management System's operations, covering all user roles, workflows, and system interactions. Each diagram can be rendered using Mermaid in compatible markdown viewers or documentation platforms.

**Key Takeaways:**
- ✅ Role-based access control with 5 distinct user types
- ✅ Complete appointment lifecycle from booking to completion
- ✅ Prescription management with PDF generation
- ✅ Real-time notification system
- ✅ Medicine inventory tracking with alerts
- ✅ Secure authentication using JWT tokens
- ✅ Comprehensive error handling
- ✅ Patient chatbot for medical queries

---

**Document Version**: 1.0  
**Compatible with**: Mermaid 9.x+  
**Last Updated**: February 17, 2026
