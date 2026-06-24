from flask import Blueprint, redirect, render_template, url_for, request, flash, session
from utils.decorators import is_logged_in
from .models import cancel_booking, create_booking

booking_bp = Blueprint('booking', __name__)

@booking_bp.route('/book-event/<int:event_id>', methods=['POST'])
@is_logged_in
def book_event(event_id):
    if session.get("role") == 'admin':
        flash("Admins cannot book tickets.", "flash-error")
        return redirect(url_for('events.events'))

    user_id = session.get('user_id')
    days_booked = request.form.get('days_booked')

    success, message = create_booking(user_id, event_id, days_booked)

    if success:
        if "waitlist" in message.lower():
            flash(message, "flash-info") 
        else:
            flash(message, "flash-success")
        return redirect(url_for('user.dashboard')) 
    else:
        flash(message, "flash-error")
        return redirect(url_for('events.event_details', event_id=event_id))

@booking_bp.route('/cancel-booking/<int:booking_id>', methods=['POST'])
@is_logged_in
def cancel_booking_route(booking_id):
    user_id = session.get('user_id')
    
    success, message = cancel_booking(booking_id, user_id)
    
    if success:
        flash(message, "flash-success")
    else:
        flash(message, "flash-error")
        
    return redirect(url_for('user.dashboard'))