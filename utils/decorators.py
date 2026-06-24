from functools import wraps
from flask import Flask, redirect, render_template, url_for, request, flash, session

def is_logged_in(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        if session.get("user_id"):
            return f(*args, **kwargs)
        else:
            flash("Please sign in", "flash-error")
            return redirect(url_for('auth.login'))
    return decorator

def is_admin(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        from users.models import get_user_by_id
        user_id = session.get("user_id")
        user_data = get_user_by_id(user_id)
        
        if user_data and user_data['role'] == 'admin':
            return f(*args, **kwargs)
        else:
            flash("You are not authorised to view this page.", "flash-error")
            return redirect(url_for('main.index'))
        
    return decorator