from flask import Blueprint, redirect, render_template, url_for, request, flash, session
from .models import *
from datetime import datetime

events_bp = Blueprint('events', __name__)

@events_bp.route('/events')
def events():
    category_id = request.args.get('category_id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    is_free = request.args.get('is_free')

    public_events = get_public_events(category_id, start_date, end_date, is_free)
    categories = get_all_categories()
    now = datetime.now()

    return render_template('events.html', events=public_events, categories=categories, now=now)

@events_bp.route("/events/<int:event_id>")
def event_details(event_id):
    event = get_event_by_id(event_id)
    total_event_days = (event['end_date'].date() - event['start_date'].date()).days + 1
    tickets_left = event['capacity'] - event['tickets_sold']
    is_sold_out = tickets_left <= 0
    status = event['status']

    now = datetime.now()
    days_until_event = (event['start_date'] - now).days
    days_until_deadline = (event['deadline'] - now).days
    deadline_passed = now >= event['booking_deadline']

    discount_multiplier = 1
    
    is_student = session.get('role') == 'student'
    
    applicable_discounts = get_applicable_discounts(event_id, days_until_event, is_student)

    if not event:
        flash("Event not found", "flash-error")
        return redirect(url_for('events.events'))
    
    if status == "draft":
        flash("Event not found.", "flash-error")
        return redirect(url_for('events.events'))

    return render_template("event-details.html", 
                           event=event,
                           total_event_days=total_event_days, 
                           tickets_left=tickets_left, 
                           is_sold_out=is_sold_out, 
                           discount_multiplier=discount_multiplier, 
                           is_student=is_student, 
                           deadline_passed=deadline_passed,
                           applicable_discounts=applicable_discounts,
                           days_until_deadline=days_until_deadline)

@events_bp.route("/category/<name>")
def category(name):
    return f"Category page for {name}"
