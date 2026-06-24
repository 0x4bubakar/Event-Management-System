from flask import Blueprint, redirect, render_template, url_for, request, flash, session
from utils.decorators import is_logged_in
from auth.models import verify_login
from users.models import create_user

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        if email and password:
            user_id, name, role, message = verify_login(email, password) 
            if user_id:
                flash(message,"flash-success")
                session["user_id"] = user_id
                session["name"] = name
                session["role"] = role
                return redirect(url_for('main.index'))
            else:
                flash(message, "flash-error")
        else:
            flash("One of the fields are missing information. Please fill them in.", "flash-error")
    return render_template('login.html')

@auth_bp.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        if name and email and password:
            user_id, role, message = create_user(name, email, password)
            if user_id:
                flash(message, "flash-success")
                session["user_id"] = user_id
                session["name"] = name
                session["role"] = role
                return redirect(url_for('main.index'))
            else:
                flash(message, "flash-error")
        else:
            flash("One of the fields are missing information. Please fill them in.", "flash-error")
    return render_template('login.html')

@auth_bp.route('/signout', methods=['GET'])
@is_logged_in
def signout():
    session.clear()
    return redirect(url_for('main.index'))