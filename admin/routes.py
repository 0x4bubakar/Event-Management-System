from flask import Blueprint, redirect, render_template, url_for, request, flash, session
from utils.decorators import is_logged_in, is_admin
from events.models import get_current_event_statuses, get_all_locations, get_all_categories, get_all_suitabilities, create_category, create_event, delete_event, create_location
from reports.models import get_revenue_reports
from .models import *
from users.models import delete_account as db_delete_account

admin_bp = Blueprint('admin', __name__)

# ADMIN HOME
@admin_bp.route('/admin', methods=['POST', 'GET'])
@is_admin
def admin_dashboard():
    event_statuses = get_current_event_statuses()
    return render_template("admin-dashboard.html", eventstat = event_statuses)

# EVENT MGMT
@admin_bp.route('/admin/events', methods=['GET'])
@is_logged_in
@is_admin
def admin_events():
    locations = get_all_locations()
    categories = get_all_categories()
    suitabilities = get_all_suitabilities() 
    events = get_all_events_admin()
    return render_template('admin-events.html', locs=locations, cats=categories, suits=suitabilities, evts=events)

# EVENT MGMT -> CREATE EVENT
@admin_bp.route('/admin/create-event', methods=['POST'])
@is_logged_in
@is_admin
def new_event():
    event_name = request.form.get("event_name")
    category_id = request.form.get("category_id")
    location_id = request.form.get("location_id")
    start_date = request.form.get("start_date")
    end_date = request.form.get("end_date")
    conditions = request.form.get("conditions")
    booking_deadline = request.form.get("booking_deadline")
    original_price = request.form.get("original_price")
    description = request.form.get("description")

    if create_event(location_id=location_id, 
        category_id=category_id, 
        organiser_id=None, # explicitly passing none as creator is an admin, not an organiser
        event_name=event_name, 
        start_date=start_date, 
        end_date=end_date, 
        conditions=conditions, 
        booking_deadline=booking_deadline, 
        description=description, 
        original_price=original_price):
        flash("Event successfully created.", "flash-success")
    else:
        flash("Failed to create event.", "flash-error")
    return redirect(url_for('admin.admin_events'))

# EVENT MGMT -> CREATE VENUE/LOCATION
@admin_bp.route('/admin/create-location', methods=['POST'])
@is_logged_in
@is_admin
def create_location_route():
    name = request.form.get("venue_name")
    address = request.form.get("address")
    capacity = request.form.get("capacity")
    suitabilities = request.form.getlist("suitabilities")

    if create_location(name, capacity, address, suitabilities):
        flash("Venue successfully created.", "flash-success")
    else:
        flash("Failed to create venue.", "flash-error")
    return redirect(url_for('admin.admin_events'))

# EVENT MGMT -> CREATE CATEGORY
@admin_bp.route('/admin/create-category', methods=['POST'])
@is_logged_in
@is_admin
def create_category_route():
    name = request.form.get("category_name")
    if create_category(name):
        flash("Category successfully created.", "flash-success")
    else:
        flash("Failed to create category.", "flash-error")
    return redirect(url_for('admin.admin_events'))

# EVENT MGMT -> DELETE EVENT
@admin_bp.route('/admin/delete-event/<int:event_id>', methods=['POST'])
@is_logged_in
@is_admin
def delete_event_route(event_id):
    if delete_event(event_id):
        flash("Event successfully deleted.", "flash-success")
    else:
        flash("Failed to delete event.", "flash-error")
    return redirect(url_for('admin.admin_events'))

# USER MGMT
@admin_bp.route('/admin/users', methods=['GET'])
@is_logged_in
@is_admin
def admin_users():
    users = get_all_users()
    return render_template('admin-users.html', users=users)

# USER MGMT -> ADMIN PASSWORD RESET
@admin_bp.route('/admin/update-password', methods=['POST'])
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

# USER MGMT -> DELETE ACCOUNT
@admin_bp.route('/admin/delete_account', methods=['POST'])
@is_logged_in
@is_admin
def admin_delete_account_route():
    target_user_id = request.form.get('user_id')
    if db_delete_account(target_user_id):
        flash("User successfully deleted.", "flash-success")
    else:
        flash("Failed to delete user.", "flash-error")
    return redirect(url_for('admin.admin_users'))