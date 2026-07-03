from flask import Blueprint, redirect, render_template, url_for, request, flash, session
from .models import get_public_events, get_all_categories, get_event_by_id
from datetime import datetime

events_bp = Blueprint('events', __name__)

@events_bp.route('/events')
def events():
    event_name = request.args.get('event_name')
    category_id = request.args.get('category_id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    is_free = request.args.get('is_free')

    public_events = get_public_events(event_name, category_id, start_date, end_date, is_free)
    categories = get_all_categories()

    return render_template('events.html', events=public_events, categories=categories)

@events_bp.route("/events/<int:event_id>")
def event_details(event_id):
    event = get_event_by_id(event_id)
    if not event:
        flash("Event not found", "flash-error")
        return redirect(url_for('events.events'))
    
    total_event_days = (event['end_date'].date() - event['start_date'].date()).days
    tickets_left = event['capacity'] - event['tickets_sold']
    is_sold_out = tickets_left <= 0

    now = datetime.now()
    days_until_event = (event['start_date'] - now).days
    deadline_passed = now >= event['booking_deadline']

    discount_multiplier = 1
    
    if days_until_event > 60:
        discount_multiplier = 0.8
    elif 50 < days_until_event <= 60:
        discount_multiplier = 0.8
    elif 35 < days_until_event <= 50:
        discount_multiplier = 0.85
    elif 25 < days_until_event <= 35:
        discount_multiplier = 0.9
    elif 15 < days_until_event <= 25:
        discount_multiplier = 0.95

    is_student = session.get('role') == 'student'

    return render_template("event-details.html", event=event, total_event_days=total_event_days, tickets_left=tickets_left, is_sold_out=is_sold_out, discount_multiplier=discount_multiplier, is_student=is_student, deadline_passed=deadline_passed) 

@events_bp.route("/category/<name>")
def category(name):
    return f"Category page for {name}"
