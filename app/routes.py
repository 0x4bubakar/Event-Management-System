import os
from app import app, models
from flask import Flask, redirect, render_template, url_for, request, flash, session
from dotenv import load_dotenv
from functools import wraps
load_dotenv()

app.secret_key = os.getenv("SECRET_KEY")

def is_logged_in(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        if session.get("user_id"):
            return f(*args, **kwargs)
        else:
            flash("Please sign in", "flash-error")
            return redirect(url_for('login'))
    return decorator

def is_admin(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        user_id = session.get("user_id")
        user_data = models.get_user_by_id(user_id)
        
        if user_data and user_data['role'] == 'admin':
            return f(*args, **kwargs)
        else:
            flash("Unauthorised access detected. Please log in.", "flash-error")
            return redirect(url_for('login'))
        
    return decorator

@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404

@app.route('/')
def index():
    if session.get("user_id"):
        return render_template('events.html')
    else:
        return render_template('index.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        if email and password:
            user_id, name, message = models.verify_login(email, password) 
            if user_id:
                flash(message,"flash-success")
                session["user_id"] = user_id
                session["name"] = name
                return redirect(url_for('index'))
            else:
                flash(message, "flash-error")
        else:
            flash("One of the fields are missing information. Please fill them in.", "flash-error")
    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        if name and email and password:
            user_id, message = models.create_user(name, email, password)
            if user_id:
                flash(message, "flash-success")
                session["user_id"] = user_id
                session["name"] = name
                return redirect(url_for('index'))
            else:
                flash(message, "flash-error")
        else:
            flash("One of the fields are missing information. Please fill them in.", "flash-error")
    return render_template('login.html')

@is_logged_in
@app.route('/signout', methods=['GET'])
def signout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/dashboard', methods=['POST', 'GET'])
@is_logged_in
def dashboard():
    user_id = session.get("user_id")
    user_data = models.get_user_by_id(user_id)

    if not user_data:
        flash("Could not load data for user profile", "flash-error")
        return redirect(url_for('index'))
    
    if user_data['role'] == 'admin':
        return redirect(render_template('admin-dashboard.html'))
    
    bookings = models.get_bookings_by_id(user_id)
        
    return render_template('user-dashboard.html', email=user_data['email'], name=user_data['name'], bookings=bookings)

@app.route('/update-profile', methods=['POST'])
@is_logged_in
def update_profile():
    user_id = session.get("user_id")
    new_email = request.form.get("email")
    new_name = request.form.get("name")
    new_password = request.form.get("password")

    # potential sanitisation logic, validation
    if not new_name or not new_email:
        flash("Name and email cannot be empty.", "flash-error")
        return redirect(url_for('dashboard'))
    
    update = models.update_user(user_id, new_name, new_email, new_password)

    if update:
        session["name"] = new_name
        flash("Account information successfully updated!", "flash-success")
        return redirect(url_for('dashboard'))
    else:
        flash("Error when updating account information. Please try again later", "flash-error")
        return redirect(url_for('dashboard'))
        
@app.route('/events')
def events():
    return render_template('events.html')

@app.route("/events/<int:event_id>")
def event_details(event_id):
    event = EVENTS.get(event_id)
    if not event:
        return "Event not found", 404
    return render_template("event-details.html", event=event) 

@app.route("/category/<name>")
def category(name):
    return f"Category page for {name}"
