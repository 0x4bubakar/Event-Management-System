from flask import Blueprint, redirect, render_template, url_for, request, flash, session
from events.models import fetch_recent_events

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    if session.get("user_id"):
        return redirect(url_for('events.events'))
    else:
        events = fetch_recent_events()
        return render_template('index.html', events=events)