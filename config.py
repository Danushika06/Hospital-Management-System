import os
from datetime import timedelta

class Config:
    """Application configuration"""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-change-in-production'
    
    # Database settings
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'database', 'hospital.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT settings
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-change-in-production'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=8)
    JWT_TOKEN_LOCATION = ['headers', 'cookies']  # Allow both headers and cookies
    JWT_COOKIE_SECURE = False  # Set to True in production with HTTPS
    JWT_COOKIE_CSRF_PROTECT = False  # Disabled for development
    JWT_CSRF_CHECK_FORM = False
    JWT_ACCESS_COOKIE_PATH = '/'
    JWT_COOKIE_SAMESITE = 'Lax'
    JWT_SESSION_COOKIE = False  # Use persistent cookies
    
    # Gemini AI API settings (deprecated)
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    
    # Groq API settings
    GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
    
    # File upload settings
    UPLOAD_FOLDER = 'static/prescriptions'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Session settings
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Application settings
    HOSPITAL_NAME = "City General Hospital"
    HOSPITAL_ADDRESS = "123 Medical Center Drive, Healthcare City"
    HOSPITAL_PHONE = "+1 (555) 123-4567"
    
    # Role definitions
    ROLES = ['admin', 'doctor', 'patient', 'receptionist', 'pharmacist']
    
    # Theme colors by role
    ROLE_COLORS = {
        'admin': '#1e3a8a',      # Deep Blue
        'doctor': '#0d9488',     # Teal
        'patient': '#16a34a',    # Green
        'receptionist': '#ea580c', # Orange
        'pharmacist': '#9333ea'  # Purple
    }
