from flask import Blueprint, redirect, render_template, url_for, request, flash, session
from .models import *
from utils.decorators import is_logged_in, is_org, is_orgs_event
from users.models import update_user, get_user_by_id

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
    return render_template('org-events.html')

@organisers_bp.route('/org/events/create', methods=['GET', 'POST'])
@is_logged_in
@is_org
def org_create_event():
    return render_template('org-dashboard.html')

@organisers_bp.route('/org/events/<int:event_id>', methods=['GET', 'POST'])
@is_logged_in
@is_org
@is_orgs_event
def org_edit_event():
    return render_template('org-dashboard.html')

@organisers_bp.route('/org/reports', methods=['GET', 'POST'])
@is_logged_in
@is_org
def org_reports():
    return render_template('org-dashboard.html')