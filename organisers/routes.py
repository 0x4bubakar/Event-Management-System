from flask import Blueprint, redirect, render_template, url_for, request, flash, session
from .models import *
from utils.decorators import is_logged_in, is_org, is_orgs_event
from users.models import update_user, get_user_by_id
from events.models import *

organisers_bp = Blueprint('org', __name__)

@organisers_bp.route('/org-register', methods=['POST', 'GET'])
def org_register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        if name and email and password:
            user_id, role, message = create_organiser(name, email, password)
            if user_id:
                flash(message, "flash-success")
                session["user_id"] = user_id
                session["name"] = name
                session["role"] = role
                return redirect(url_for('org.org_dashboard'))
            else:
                flash(message, "flash-error")
            
        else:
            flash("One of the fields are missing information. Please fill them in.", "flash-error")
        
    return render_template('org-register.html')

@organisers_bp.route('/org', methods=['GET', 'POST'])
@is_logged_in
@is_org
def org_dashboard():
    return render_template('org-dashboard.html')

@organisers_bp.route('/org/profile', methods=['GET', 'POST'])
@is_logged_in
@is_org
def org_profile():
    user_id = session.get("user_id")
    user_data = get_user_by_id(user_id)
    org_data = get_org_by_user_id(user_id)

    if request.method == 'POST':
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        description = request.form.get("description")
        
        if not name or not email:
            flash("Name and email cannot be empty.", "flash-error")
            return redirect(url_for('org.org_profile'))
        
        org_id = org_data['organiser_id']
        update_org = edit_org_profile(org_id, description)
        update_user_details = update_user(user_id, name, email, password)

        if update_user_details and update_org:
            user_data = get_user_by_id(user_id)
            session["name"] = name
            session["role"] = update_user_details["role"]
            flash("Account information successfully updated!", "flash-success")
            return redirect(url_for('org.org_profile'))
        else:
            flash("Error when updating account information. Please try again later", "flash-error")
            return redirect(url_for('org.org_profile'))
        
    email = user_data['email']
    name = user_data['name']
    description = org_data['description']
    return render_template('org-profile.html', email=email, name=name, description=description)

@organisers_bp.route('/org/events', methods=['GET', 'POST'])
@is_logged_in
@is_org
def org_events():
    user_id = session.get("user_id")
    org_data = get_org_by_user_id(user_id)
    org_id = org_data['organiser_id']
    locations = get_all_locations()
    categories = get_all_categories()
    suitabilities = get_all_suitabilities() 
    events = get_all_events_org(org_id)
    return render_template('org-events.html', locs=locations, cats=categories, suits=suitabilities, evts=events)

@organisers_bp.route('/org/events/create', methods=['GET', 'POST'])
@is_logged_in
@is_org
def org_create_event():
    user_id = session.get("user_id")
    org_data = get_org_by_user_id(user_id)
    org_id = org_data['organiser_id']
    locations = get_all_locations()
    categories = get_all_categories()
    suitabilities = get_all_suitabilities()

    if request.method == 'POST':
        event_name = request.form.get("event_name")
        category_id = request.form.get("category_id")
        location_id = request.form.get("location_id")
        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date")
        conditions = request.form.get("conditions")
        booking_deadline = request.form.get("booking_deadline")
        original_price = request.form.get("original_price")
        description = request.form.get("description")
        try:
            tickets = int(request.form.get("tickets"))
        except Exception as e:
            flash(f"Error with tickets: {e}", "flash-error")
        loc = get_location_by_id(location_id)

        dates_are_valid, error_msg = validate_event_dates(start_date, end_date, booking_deadline)
        if not dates_are_valid:
            flash(error_msg, "flash-error")
            return redirect(url_for('org.org_create_event'))
        
        if location_id and category_id:
            if not is_location_suitable(location_id, category_id):
                flash("The venue is not suitable for the chosen event category.")
                return redirect(url_for('org.org_create_event'))
        
        if tickets > loc['capacity']:
            flash("The event cannot have a number of tickets greater than the capacity of the location.", "flash-error")
            return redirect(url_for('org.org_create_event'))

        if not isinstance(tickets, int) or tickets <= 0:
            flash("Number of tickets must be a positive integer.", "flash-error")
            return redirect(url_for('org.org_create_event'))
        
        event_id = create_event(location_id=location_id, 
            category_id=category_id, 
            event_name=event_name, 
            start_date=start_date, 
            end_date=end_date, 
            conditions=conditions, 
            booking_deadline=booking_deadline, 
            description=description, 
            original_price=original_price,
            tickets=tickets,
            organiser_id=org_id) 
        
        if event_id is not None:
            flash("Event successfully created.", "flash-success")
            return redirect(url_for('org.org_pay_fee'), event_id=event_id)
        else:
            flash("Failed to create event.", "flash-error")


    return render_template('org-create-event.html', locs=locations, cats=categories, suits=suitabilities)

@organisers_bp.route('/org/events/<int:event_id>/pay-fee', methods=['GET', 'POST'])
@is_logged_in
@is_org
@is_orgs_event
def org_pay_fee(event_id):
    if event_id:
        if request.method == 'POST':
            if publish_draft_event(event_id):
                flash("Event succesfully published.", "flash-success")
                return redirect(url_for('org.org_events'))
            else:
                flash("Error publishing event.", "flash-error")
                return redirect(url_for('org.org_events'))
    
    event_data = get_event_by_id(event_id)
    if event_data:
        return render_template('org-pay-fee.html', evt=event_data)
    
    flash("You are unauthorised to view this page.")
    return redirect(url_for('org.org_events'))

@organisers_bp.route('/org/events/<int:event_id>', methods=['GET', 'POST'])
@is_logged_in
@is_org
@is_orgs_event
def org_edit_event(event_id):
    if request.method == 'POST':
        event_name = request.form.get("event_name")
        category_id = request.form.get("category_id")
        location_id = request.form.get("location_id")
        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date")
        conditions = request.form.get("conditions")
        booking_deadline = request.form.get("booking_deadline")
        original_price = request.form.get("original_price")
        description = request.form.get("description")
        tickets = request.form.get("tickets")

        dates_are_valid, error_msg = validate_event_dates(start_date, end_date, booking_deadline)
        if not dates_are_valid:
            flash(error_msg, "flash-error")
            return redirect(url_for('org.org_edit_event'))
        
        if not tickets:
            flash("Please input a number of tickets", "flash-error")
            return redirect(url_for('org.org_edit_event', event_id=event_id))

        if location_id and category_id:
            if not is_location_suitable(location_id, category_id):
                flash("The venue is not suitable for the chosen event category.")
                return redirect(url_for('org.org_edit_event', event_id=event_id))
        if edit_events(location_id=location_id, 
            category_id=category_id, 
            event_name=event_name, 
            start_date=start_date, 
            end_date=end_date, 
            conditions=conditions, 
            booking_deadline=booking_deadline, 
            description=description, 
            original_price=original_price,
            event_id=event_id,
            tickets=tickets):
            flash("Event successfully edited.", "flash-success")
            return redirect(url_for('org.org_events'))
        else:
            flash("Failed to edit event.", "flash-error")
    
    event_data = get_event_by_id(event_id)
    locations = get_all_locations()
    categories = get_all_categories()
    suitabilities = get_all_suitabilities()

    return render_template('org-edit-event.html', event_id=event_id, 
                           event=event_data,
                           locs=locations,
                           cats=categories,
                           suits=suitabilities)

@organisers_bp.route('/org/reports', methods=['GET', 'POST'])
@is_logged_in
@is_org
def org_reports():
    return render_template('org-dashboard.html')