from functools import wraps
from flask import jsonify, request, redirect, url_for, flash, session
from models import User

def role_required(*roles):
    """Decorator to require specific roles for routes"""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # Check session for user_id
            user_id = session.get('user_id')
            
            if not user_id:
                flash('Please login to access this page.', 'warning')
                return redirect(url_for('login'))
            
            user = User.query.get(user_id)
            
            if not user:
                session.clear()
                flash('User not found. Please login again.', 'danger')
                return redirect(url_for('login'))
            
            if not user.is_active:
                session.clear()
                flash('Your account has been deactivated. Please contact administrator.', 'danger')
                return redirect(url_for('login'))
            
            if user.role not in roles:
                flash('Access denied. You do not have permission to access this page.', 'danger')
                return redirect(url_for(f'{user.role}.dashboard'))
            
            return fn(*args, **kwargs)
        
        return wrapper
    return decorator


def get_current_user():
    """Get the current logged-in user"""
    user_id = session.get('user_id')
    if user_id:
        return User.query.get(user_id)
    return None


def login_required(fn):
    """Decorator to require any authenticated user"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user_id = session.get('user_id')
        
        if not user_id:
            flash('Please login to continue.', 'warning')
            return redirect(url_for('login'))
        
        user = User.query.get(user_id)
        
        if not user:
            session.clear()
            flash('Please login to continue.', 'warning')
            return redirect(url_for('login'))
        
        if not user.is_active:
            session.clear()
            flash('Your account has been deactivated.', 'danger')
            return redirect(url_for('login'))
        
        return fn(*args, **kwargs)
    
    return wrapper


def validate_input(data, required_fields):
    """Validate that required fields are present and not empty"""
    missing_fields = []
    
    for field in required_fields:
        if field not in data or not data[field] or str(data[field]).strip() == '':
            missing_fields.append(field)
    
    if missing_fields:
        return False, f"Missing or empty fields: {', '.join(missing_fields)}"
    
    return True, "Valid"


def is_safe_redirect_url(target):
    """Check if a redirect URL is safe (prevents open redirect vulnerabilities)"""
    if not target:
        return False
    
    # Only allow relative URLs
    if target.startswith('/') and not target.startswith('//'):
        return True
    
    return False
