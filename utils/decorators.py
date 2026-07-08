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

def is_org(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        from users.models import get_user_by_id
        user_id = session.get("user_id")
        user_data = get_user_by_id(user_id)
        
        if user_data and user_data['role'] == 'organiser':
            return f(*args, **kwargs)
        else:
            flash("You are not authorised to view this page.", "flash-error")
            return redirect(url_for('main.index'))
        
    return decorator

def is_orgs_event(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        from events.models import get_event_by_id
        from organisers.models import get_org_by_user_id
        user_id = session.get("user_id")
        event_id = kwargs.get('event_id')
        org_id = get_org_by_user_id(user_id)
        event = get_event_by_id(event_id)

        if org_id == event['organiser_id']:
            return f(*args, **kwargs)
        else:
            flash("You are not authorised to view this page.", "flash-error")
            return redirect(url_for('main.index'))
        
    return decorator