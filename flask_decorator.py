from functools import wraps
from flask import session, redirect, url_for, flash

def admin_required(f):
    """
    Decorator for routes that require admin authentication.
    Redirects to admin login page if not authenticated.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            flash('Please login to access admin area', 'warning')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function 