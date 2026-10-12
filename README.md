# Hospital Management System

**A role-based Flask web app for running a small hospital's day-to-day flow: patients book appointments, receptionists approve them, doctors issue prescriptions as PDFs, pharmacists dispense them and manage stock, and an admin manages users.**

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white) ![Flask](https://img.shields.io/badge/Flask-000000?style=flat&logo=flask&logoColor=white) ![SQLite](https://img.shields.io/badge/SQLite-003B57?style=flat&logo=sqlite&logoColor=white) ![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?style=flat&logo=sqlalchemy&logoColor=white) ![JWT](https://img.shields.io/badge/JWT-000000?style=flat&logo=jsonwebtokens&logoColor=white) ![Groq](https://img.shields.io/badge/Groq-F55036?style=flat) ![Chart.js](https://img.shields.io/badge/Chart.js-FF6384?style=flat&logo=chartdotjs&logoColor=white) ![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=flat&logo=html5&logoColor=white)

## Overview

A hospital visit passes through several people: the patient asks for a slot, the front desk confirms it, the doctor sees the patient and writes a prescription, and the pharmacy hands out the medicine. If each step lives in a different notebook or spreadsheet, nobody knows where a request is stuck.

This project puts those five roles into one Flask application. Each role gets its own blueprint, dashboard and templates, and the steps hand off to each other through appointment and prescription statuses and in-app notifications. There is also a patient-facing chatbot backed by the Groq API.

Status: it is a working prototype on SQLite with seeded demo users, built as a learning project. The hospital name, address and phone number are placeholders in `config.py`. Prescriptions are free text, and the medicine inventory is a separate table that dispensing does not touch, so stock is not reduced when a prescription is dispensed. The chatbot gives general information only and is not medical advice. The repo also contains four long Markdown documentation files that I did not use as a source for this README.

## Key Features

- **Five roles with separate areas** - admin, doctor, patient, receptionist and pharmacist, each a Flask blueprint under its own URL prefix (`/admin`, `/doctor`, `/patient`, `/receptionist`, `/pharmacist`). The `role_required` decorator in `auth.py` checks the session user, rejects deactivated accounts, and bounces a wrong-role user to their own dashboard.
- **Appointment workflow** - a patient books a slot with an active doctor (past dates are refused) and the status starts as `Pending`. A receptionist approves, rejects or reschedules it, and each step creates notifications for the people involved.
- **Prescriptions as PDFs** - a doctor issues a prescription for one of their own appointments (diagnosis plus medicines), which marks the appointment `Completed`. `services/pdf_service.py` renders the prescription to a PDF with ReportLab into `static/prescriptions/`, and patients can download it.
- **Pharmacy desk** - the pharmacist sees pending prescriptions, marks them `Dispensed` (which notifies the patient), and manages medicine inventory with add, update, restock and delete, plus dispensing history, low-stock alerts and expiry tracking pages. `Medicine.is_low_stock` uses a threshold of 50.
- **Notifications** - a `Notification` table with read/unread state, created by the booking, approval, prescription and dispensing steps. Each role has a notifications page, and the unread count is injected into every template by a context processor in `app.py`.
- **Patient analytics** - `patient.analytics` counts the patient's appointments, prescriptions and most frequent medicines and shows appointments for the last six months in a Chart.js chart.
- **Admin tools** - add, deactivate and delete users, list all appointments and prescriptions, and copy the SQLite file to a timestamped backup from the dashboard (`/admin/backup_database`).
- **AI chatbot** - `/api/chatbot` calls `services/chatbot_service.py`, which sends the question with a hospital system prompt to Groq's `llama-3.3-70b-versatile` model. Messages containing emergency keywords (chest pain, stroke, overdose and similar) skip the model and return a fixed "call emergency services" reply.

## How It Works

**Startup.** `app.py` loads `.env`, builds the Flask app from `config.Config`, and registers the five blueprints. On first run `db.create_all()` creates the tables in `database/hospital.db`, and if no `admin` user exists it seeds one user per role plus five sample medicines. The seeded usernames and passwords are in `app.py` and printed to the console on first start, so change them before putting this anywhere real.

**Sign-in.** `/login` checks the username and password hash (`werkzeug` PBKDF2) and stores `user_id` and `user_role` in the Flask session, then redirects to the role's dashboard. The app is configured with Flask-JWT-Extended (8-hour tokens, header and cookie locations), but the login route does not issue a token. Page access runs on the session. The only route that uses `@jwt_required` is `/api/notifications/<user_id>`, so with the current login flow it is effectively unreachable from the web UI.

**Data model** (`models.py`): `User` (role, active flag, hashed password), `Appointment` (patient, doctor, date, time, status `Pending/Approved/Rejected/Completed`), `Prescription` (appointment, doctor, patient, diagnosis, `medicine_details` as text, `issued_status` `Pending/Dispensed`), `Medicine` (name, quantity, expiry date) and `Notification`.

**Typical flow.**

1. Patient: `book_appointment` creates a `Pending` appointment and notifies every active receptionist.
2. Receptionist: `approve_appointment` sets `Approved` and notifies the patient and the doctor.
3. Doctor: `issue_prescription` creates the prescription, sets the appointment to `Completed`, notifies the patient and all pharmacists.
4. Pharmacist: `dispense_prescription` sets `Dispensed` and tells the patient it is ready for pickup.

## Tech Stack

- **Language / framework:** Python, Flask 2.3.0
- **Database:** SQLite through Flask-SQLAlchemy 3.0.5
- **Auth:** Flask sessions with Werkzeug password hashing; Flask-JWT-Extended 4.5.2 is configured but only guards one route
- **PDF:** ReportLab 4.0.4
- **AI:** Groq Python client (model `llama-3.3-70b-versatile`)
- **Config:** python-dotenv
- **Frontend:** Jinja2 templates, plain CSS (`static/css/style.css`), vanilla JavaScript (`static/js/script.js`), Chart.js from a CDN

## Getting Started

### Prerequisites
- Python 3 and `pip`
- A Groq API key if you want the chatbot to answer (the rest of the app runs without it, but `services/chatbot_service.py` creates the Groq client when it is imported, so check that the app starts cleanly without a key)

### Installation
```bash
git clone https://github.com/Danushika06/Hospital-Management-System.git
cd Hospital-Management-System
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```
Edit `.env` and set `SECRET_KEY`, `JWT_SECRET_KEY` and `GROQ_API_KEY`. The template also lists `GEMINI_API_KEY`, which `config.py` marks as deprecated and the chatbot no longer uses.

### Running
```bash
python app.py
```
The app creates `database/` and `static/prescriptions/` if they are missing and serves on `http://localhost:5000` (debug mode, bound to `0.0.0.0`). Log in with one of the seeded users from `app.py`.

## Usage

| Role | Pages |
|------|-------|
| Patient | dashboard, book appointment, appointments, prescriptions (PDF download), analytics, chatbot, profile, notifications |
| Receptionist | dashboard, appointments, approve / reject / reschedule, queue, notify doctor, notifications |
| Doctor | dashboard, appointments, patient history, issue prescription, prescriptions, notifications |
| Pharmacist | dashboard, prescriptions, dispense, inventory (add / update / restock / delete), dispensing history, low-stock alerts, expiry tracking, notifications |
| Admin | dashboard, users (add / deactivate / delete), appointments, prescriptions, database backup |

Non-page endpoints in `app.py`:

| Method | Route | Purpose |
|--------|-------|---------|
| GET, POST | `/login` | Sign in |
| GET | `/logout` | Clear the session |
| POST | `/api/chatbot` | Body: `message`, optional `type` (`general`, `symptom`, `medicine`, `appointment`, `faq`, `emergency`) and `role`; returns the reply as JSON |
| GET | `/api/notifications/<user_id>` | Last 10 notifications; requires a JWT |

The chatbot endpoint does not check the session, so anyone who can reach the server can call it.

## Project Structure

```
Hospital-Management-System/
├── app.py                  # app factory, DB seeding, login/logout, chatbot + notifications APIs
├── config.py               # Flask, SQLite, JWT, upload and role-colour settings
├── models.py               # User, Appointment, Prescription, Medicine, Notification
├── auth.py                 # role_required, login_required, input validation helpers
├── routes/                 # one blueprint per role
│   ├── admin.py
│   ├── doctor.py
│   ├── patient.py
│   ├── pharmacist.py
│   └── receptionist.py
├── services/
│   ├── chatbot_service.py  # Groq chatbot with emergency keyword shortcut
│   └── pdf_service.py      # prescription PDF generation (ReportLab)
├── templates/              # base layout, login, error pages, one folder per role
├── static/                 # css, js, generated prescription PDFs
├── requirements.txt
└── .env.example
```

The root also holds four long Markdown documents (system overview, flow documentation, flow diagrams, quick reference).

---

## Contact

<table>
  <tr><td><b>GitHub:</b> <a href="https://github.com/Danushika06">Danushika06</a></td><td><b>LinkedIn:</b> <a href="https://www.linkedin.com/in/danushika-n-323b4628b/">danushika-n</a></td></tr>
  <tr><td colspan="2" align="center"><b>Email:</b> <a href="mailto:danushikanagarajan@gmail.com">danushikanagarajan@gmail.com</a></td></tr>
</table>

Built by **Danushika N**
