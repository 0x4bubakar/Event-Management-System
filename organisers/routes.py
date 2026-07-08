from flask import Blueprint, redirect, render_template, url_for, request, flash, session
from .models import *
from utils.decorators import is_logged_in, is_org, is_orgs_event

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
                return redirect(url_for('users.dashboard'))
            else:
                flash(message, "flash-error")
            
        else:
            flash("One of the fields are missing information. Please fill them in.", "flash-error")
        
    return render_template('org-register.html')

@organisers_bp.route('/org', methods=['GET', 'POST'])
@is_logged_in
@is_org
def org_dashboard():
    return render_template('org_dashboard.html')

@organisers_bp.route('/org/events', methods=['GET', 'POST'])
@is_logged_in
@is_org
def org_events():
    return render_template('org_dashboard.html')

@organisers_bp.route('/org/events/create', methods=['GET', 'POST'])
@is_logged_in
@is_org
def org_create_event():
    return render_template('org_dashboard.html')

@organisers_bp.route('/org/events/<int:event_id>', methods=['GET', 'POST'])
@is_logged_in
@is_org
@is_orgs_event
def org_edit_event():
    return render_template('org_dashboard.html')