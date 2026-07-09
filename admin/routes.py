from flask import Blueprint, redirect, render_template, url_for, request, flash, session
from utils.decorators import is_logged_in, is_admin
from events.models import get_all_locations, get_all_categories, get_all_suitabilities, get_event_by_id, create_category, create_event, delete_event, create_location, edit_events, is_location_suitable, validate_event_dates, edit_location, get_location_by_id
from reports.models import get_revenue_reports
from .models import *
from users.models import delete_account as db_delete_account

admin_bp = Blueprint('admin', __name__)

# Admin dashboard
@admin_bp.route('/admin', methods=['POST', 'GET'])
@is_admin
def admin_dashboard():
    quickstats = get_quick_stats()
    return render_template("admin-dashboard.html", quickstats=quickstats)

# Event management
@admin_bp.route('/admin/events', methods=['GET'])
@is_logged_in
@is_admin
def admin_events():
    locations = get_all_locations()
    categories = get_all_categories()
    suitabilities = get_all_suitabilities() 
    events = get_all_events_admin()
    return render_template('admin-events.html', locs=locations, cats=categories, suits=suitabilities, evts=events)

@admin_bp.route('/admin/events/create', methods=['GET','POST'])
@is_logged_in
@is_admin
def new_event():
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
        tickets = request.form.get("tickets")
        try:
            tickets = int(request.form.get("tickets"))
        except (TypeError, ValueError):
            tickets =y
        loc = get_location_by_id(location_id)

        dates_are_valid, error_msg = validate_event_dates(start_date, end_date, booking_deadline)
        if not dates_are_valid:
            flash(error_msg, "flash-error")
            return redirect(url_for('admin.new_event'))
        
        if location_id and category_id:
            if not is_location_suitable(location_id, category_id):
                flash("The venue is not suitable for the chosen event category.")
                return redirect(url_for('admin.new_event'))
        
        if tickets > loc['capacity']:
            flash("The event cannot have a number of tickets greater than the capacity of the location.", "flash-error")
            return redirect(url_for('admin.new_event'))

        if not isinstance(tickets, int) or tickets <= 0:
            flash("Number of tickets must be a positive integer.", "flash-error")
            return redirect(url_for('admin.new_event'))

        if create_event(location_id=location_id, 
            category_id=category_id, 
            organiser_id=None, # explicitly passing none as creator is an admin, not an organiser
            event_name=event_name, 
            start_date=start_date, 
            end_date=end_date, 
            conditions=conditions, 
            booking_deadline=booking_deadline, 
            description=description, 
            original_price=original_price,
            tickets=tickets):
            flash("Event successfully created.", "flash-success")
            return redirect(url_for('admin.admin_events'))
        else:
            flash("Failed to create event.", "flash-error")

    return render_template('admin-create-event.html', locs = locations, cats = categories, suits = suitabilities)

@admin_bp.route('/admin/events/<int:event_id>', methods=['GET', 'POST'])
@is_logged_in
@is_admin
def edit_event_route(event_id):
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

        dates_are_valid, error_msg = validate_event_dates(start_date, end_date, booking_deadline)
        if not dates_are_valid:
            flash(error_msg, "flash-error")
            return redirect('admin.edit_event_route')
        
        if location_id and category_id:
            if not is_location_suitable(location_id, category_id):
                flash("The venue is not suitable for the chosen event category.")
                return redirect(url_for('admin.edit_event_route', event_id=event_id))
        if edit_events(location_id=location_id, 
            category_id=category_id, 
            organiser_id=None,
            event_name=event_name, 
            start_date=start_date, 
            end_date=end_date, 
            conditions=conditions, 
            booking_deadline=booking_deadline, 
            description=description, 
            original_price=original_price,
            event_id=event_id):
            flash("Event successfully edited.", "flash-success")
            return redirect(url_for('admin.admin_events'))
        else:
            flash("Failed to edit event.", "flash-error")
    
    event_data = get_event_by_id(event_id)
    locations = get_all_locations()
    categories = get_all_categories()
    suitabilities = get_all_suitabilities()

    return render_template('admin-edit-event.html', 
                           event_id=event_id, 
                           event=event_data,
                           locs=locations,
                           cats=categories,
                           suits=suitabilities)

@admin_bp.route('/admin/events/delete/<int:event_id>', methods=['POST'])
@is_logged_in
@is_admin
def delete_event_route(event_id):
    if delete_event(event_id):
        flash("Event successfully deleted.", "flash-success")
    else:
        flash("Failed to delete event.", "flash-error")
    return redirect(url_for('admin.admin_events'))


# Venue management
@admin_bp.route('/admin/locations', methods=['GET'])
@is_logged_in
@is_admin
def locations_route():
    locations = get_all_locations()
    suitabilities = get_all_suitabilities
    return render_template('admin-locations.html',
                            locs = locations,
                            suits = suitabilities)

@admin_bp.route('/admin/locations/create', methods=['GET', 'POST'])
@is_logged_in
@is_admin
def create_location_route():
    if request.method == 'POST':
        name = request.form.get("venue_name")
        address = request.form.get("address")
        capacity = request.form.get("capacity")
        suitabilities = request.form.getlist("suitabilities")

        if create_location(name, capacity, address, suitabilities):
            flash("Venue successfully created.", "flash-success")
        else:
            flash("Failed to create venue.", "flash-error")
    locations = get_all_locations()
    categories = get_all_categories()
    return render_template('admin-create-location.html',
                           locs = locations,
                           cats = categories)

@admin_bp.route('/admin/locations/<int:location_id>', methods=['GET', 'POST'])
@is_logged_in
@is_admin
def edit_location_route(location_id):
    if request.method == 'POST':
        name = request.form.get("venue_name")
        address = request.form.get("address")
        capacity = request.form.get("capacity")
        suitabilities = request.form.getlist("suitabilities")

        if edit_location(name, capacity, address, suitabilities, location_id):
            flash("Venue successfully edited.", "flash-success")
        else:
            flash("Failed to edit venue.", "flash-error")
    
    location_data = get_location_by_id(location_id)
    categories = get_all_categories()
    suitabilities = get_all_suitabilities()
    
    current_suits = [suit['category_id'] for suit in suitabilities if suit['location_id'] == location_id]
    
    return render_template('admin-edit-location.html', location_id=location_id, loc=location_data, cats=categories, current_suits=current_suits)


# Categories management
@admin_bp.route('/admin/categories', methods=['GET'])
@is_logged_in
@is_admin
def categories_route():
    categories = get_all_categories()
    return render_template('admin-categories.html', cats=categories)

@admin_bp.route('/admin/categories/create', methods=['GET','POST'])
@is_logged_in
@is_admin
def create_category_route():
    if request.method == 'POST':
        name = request.form.get("category_name")
        if create_category(name):
            flash("Category successfully created.", "flash-success")
            return redirect(url_for('admin.categories_route'))
        else:
            flash("Failed to create category.", "flash-error")

    return render_template('admin-create-category.html')

@admin_bp.route('/admin/categories/delete', methods=['POST'])
@is_logged_in
@is_admin
def admin_delete_category_route():
    target_cat_id = request.form.get('cat_id')
    if db_delete_category(target_cat_id):
        flash("Category successfully deleted.", "flash-success")
    else:
        flash("Failed to delete category.", "flash-error")
    return redirect(url_for('admin.categories_route'))


# User management
@admin_bp.route('/admin/users', methods=['GET'])
@is_logged_in
@is_admin
def admin_users():
    users = get_all_users()
    return render_template('admin-users.html', users=users)

@admin_bp.route('/admin/users/update-password', methods=['POST'])
@is_logged_in
@is_admin
def admin_update_password_route():
    target_user_id = request.form.get('user_id')
    new_password = request.form.get('new_password')
    if admin_update_password(target_user_id, new_password):
        flash("User password successfully overwritten.", "flash-success")
    else:
        flash("Failed to update password.", "flash-error")
    return redirect(url_for('admin.admin_users'))

@admin_bp.route('/admin/users/delete', methods=['POST'])
@is_logged_in
@is_admin
def admin_delete_account_route():
    target_user_id = request.form.get('user_id')
    if db_delete_account(target_user_id):
        flash("User successfully deleted.", "flash-success")
    else:
        flash("Failed to delete user.", "flash-error")
    return redirect(url_for('admin.admin_users'))