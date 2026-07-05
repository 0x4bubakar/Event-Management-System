from flask import Blueprint, redirect, render_template, url_for, request, flash, session
from .models import get_user_by_id, update_user, get_bookings_by_id
from .models import delete_account as db_delete_account
from utils.decorators import is_logged_in

users_bp = Blueprint('users', __name__)

@users_bp.route('/dashboard', methods=['POST', 'GET'])
@is_logged_in
def dashboard():
    user_id = session.get("user_id")
    user_data = get_user_by_id(user_id)

    if not user_data:
        flash("Could not load data for user profile", "flash-error")
        return redirect(url_for('main.index'))
    
    if user_data['role'] == 'admin':
        return redirect(url_for('admin.admin_dashboard'))
    
    bookings = get_bookings_by_id(user_id)
        
    return render_template('user-dashboard.html', email=user_data['email'], name=user_data['name'], bookings=bookings)

@users_bp.route('/update-profile', methods=['POST'])
@is_logged_in
def update_profile():
    user_id = session.get("user_id")
    new_email = request.form.get("email")
    new_name = request.form.get("name")
    new_password = request.form.get("password")

    if not new_name or not new_email:
        flash("Name and email cannot be empty.", "flash-error")
        return redirect(url_for('users.dashboard'))
    
    update = update_user(user_id, new_name, new_email, new_password)

    if update:
        user_data = get_user_by_id(user_id)
        session["name"] = new_name
        session["role"] = user_data["role"]
        flash("Account information successfully updated!", "flash-success")
        return redirect(url_for('users.dashboard'))
    else:
        flash("Error when updating account information. Please try again later", "flash-error")
        return redirect(url_for('users.dashboard'))

@users_bp.route('/delete_account', methods=['POST'])
@is_logged_in
def delete_account():
    target_user_id = session.get('user_id')
    if target_user_id:
        if db_delete_account(target_user_id):
            flash("Account successfully deleted.", "flash-success")
            session.clear()
        else:
            flash("Failed to delete account.", "flash-error")
    return redirect(url_for('main.index'))

