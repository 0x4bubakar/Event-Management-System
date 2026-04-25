import os
from app import app, models
from flask import Flask, redirect, render_template, url_for, request, flash, session
from dotenv import load_dotenv
from functools import wraps
from datetime import datetime
load_dotenv()

app.secret_key = os.getenv("SECRET_KEY")

# ========== AUTH LOGIC ==========

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

# ========== END OF AUTH LOGIC ==========

# ========== ERROR HANDLING LOGIC ==========

@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404

# ========== END OF ERROR HANDLING LOGIC ==========

# ========== USER LOGIC ==========

@app.route('/')
def index():
    if session.get("user_id"):
        return render_template('events.html')
    else:
        events = models.fetch_recent_events()
        return render_template('index.html', events=events)

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        if email and password:
            user_id, name, role, message = models.verify_login(email, password) 
            if user_id:
                flash(message,"flash-success")
                session["user_id"] = user_id
                session["name"] = name
                session["role"] = role
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
            user_id, role, message = models.create_user(name, email, password)
            if user_id:
                flash(message, "flash-success")
                session["user_id"] = user_id
                session["name"] = name
                session["role"] = role
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
        return redirect(url_for('admin_dashboard'))
    
    bookings = models.get_bookings_by_id(user_id)
        
    return render_template('user-dashboard.html', email=user_data['email'], name=user_data['name'], bookings=bookings)

@app.route('/cancel-booking/<int:booking_id>', methods=['POST'])
@is_logged_in
def cancel_booking_route(booking_id):
    user_id = session.get('user_id')
    
    success, message = models.cancel_booking(booking_id, user_id)
    
    if success:
        flash(message, "flash-success")
    else:
        flash(message, "flash-error")
        
    return redirect(url_for('dashboard'))

@app.route('/update-profile', methods=['POST'])
@is_logged_in
def update_profile():
    user_id = session.get("user_id")
    new_email = request.form.get("email")
    new_name = request.form.get("name")
    new_password = request.form.get("password")

    if not new_name or not new_email:
        flash("Name and email cannot be empty.", "flash-error")
        return redirect(url_for('dashboard'))
    
    update = models.update_user(user_id, new_name, new_email, new_password)

    if update:
        user_data = models.get_user_by_id(user_id)
        session["name"] = new_name
        session["role"] = user_data["role"]
        flash("Account information successfully updated!", "flash-success")
        return redirect(url_for('dashboard'))
    else:
        flash("Error when updating account information. Please try again later", "flash-error")
        return redirect(url_for('dashboard'))
    

@app.route('/delete_account', methods=['POST'])
@is_logged_in
def delete_account():
    target_user_id = session.get('user_id')
    if target_user_id:
        if models.delete_account(target_user_id):
            flash("Account successfully deleted.", "flash-success")
            session.clear()
        else:
            flash("Failed to delete account.", "flash-error")
    return redirect(url_for('index'))

@app.route('/book-event/<int:event_id>', methods=['POST'])
@is_logged_in
def book_event(event_id):
    if session.get("role") == 'admin':
        flash("Admins cannot book tickets.", "flash-error")
        return redirect(url_for('events'))

    user_id = session.get('user_id')
    days_booked = request.form.get('days_booked')

    success, message = models.create_booking(user_id, event_id, days_booked)

    if success:
        if "waitlist" in message.lower():
            flash(message, "flash-info") 
        else:
            flash(message, "flash-success")
        return redirect(url_for('dashboard')) 
    else:
        flash(message, "flash-error")
        return redirect(url_for('event_details', event_id=event_id))

# ========== END OF USER LOGIC ==========

# ========== ADMIN LOGIC ==========

# ADMIN HOME
@app.route('/admin', methods=['POST', 'GET'])
@is_admin
def admin_dashboard():
    event_statuses = models.get_current_event_statuses()
    return render_template("admin-dashboard.html", eventstat = event_statuses)

# EVENT MGMT
@app.route('/admin/events', methods=['GET'])
@is_logged_in
@is_admin
def admin_events():
    locations = models.get_all_locations()
    categories = models.get_all_categories()
    suitabilities = models.get_all_suitabilities() 
    events = models.get_all_events_admin()
    return render_template('admin-events.html', locs=locations, cats=categories, suits=suitabilities, evts=events)

# EVENT MGMT -> CREATE EVENT
@app.route('/admin/create-event', methods=['POST'])
@is_logged_in
@is_admin
def create_event():
    event_name = request.form.get("event_name")
    category_id = request.form.get("category_id")
    location_id = request.form.get("location_id")
    start_date = request.form.get("start_date")
    end_date = request.form.get("end_date")
    conditions = request.form.get("conditions")
    booking_deadline = request.form.get("booking_deadline")
    original_price = request.form.get("original_price")
    description = request.form.get("description")

    if models.create_event(location_id, event_name, start_date, end_date, conditions, booking_deadline, description, category_id, original_price):
        flash("Event successfully created.", "flash-success")
    else:
        flash("Failed to create event.", "flash-error")
    return redirect(url_for('admin_events'))

# EVENT MGMT -> CREATE VENUE/LOCATION
@app.route('/admin/create-location', methods=['POST'])
@is_logged_in
@is_admin
def create_location():
    name = request.form.get("venue_name")
    address = request.form.get("address")
    capacity = request.form.get("capacity")
    suitabilities = request.form.getlist("suitabilities")

    if models.create_location(name, capacity, address, suitabilities):
        flash("Venue successfully created.", "flash-success")
    else:
        flash("Failed to create venue.", "flash-error")
    return redirect(url_for('admin_events'))

# EVENT MGMT -> CREATE CATEGORY
@app.route('/admin/create-category', methods=['POST'])
@is_logged_in
@is_admin
def create_category():
    name = request.form.get("category_name")
    if models.create_category(name):
        flash("Category successfully created.", "flash-success")
    else:
        flash("Failed to create category.", "flash-error")
    return redirect(url_for('admin_events'))

# EVENT MGMT -> DELETE EVENT
@app.route('/admin/delete-event/<int:event_id>', methods=['POST'])
@is_logged_in
@is_admin
def delete_event_route(event_id):
    if models.delete_event(event_id):
        flash("Event successfully deleted.", "flash-success")
    else:
        flash("Failed to delete event.", "flash-error")
    return redirect(url_for('admin_events'))

# USER MGMT
@app.route('/admin/users', methods=['GET'])
@is_logged_in
@is_admin
def admin_users():
    users = models.get_all_users()
    return render_template('admin-users.html', users=users)

# USER MGMT -> ADMIN PASSWORD RESET
@app.route('/admin/update-password', methods=['POST'])
@is_logged_in
@is_admin
def admin_update_password():
    target_user_id = request.form.get('user_id')
    new_password = request.form.get('new_password')
    if models.admin_update_password(target_user_id, new_password):
        flash("User password successfully overwritten.", "flash-success")
    else:
        flash("Failed to update password.", "flash-error")
    return redirect(url_for('admin_users'))

# USER MGMT -> DELETE ACCOUNT
@app.route('/admin/delete_account', methods=['POST'])
@is_logged_in
@is_admin
def admin_delete_account():
    target_user_id = request.form.get('user_id')
    if models.admin_delete_account(target_user_id):
        flash("User successfully deleted.", "flash-success")
    else:
        flash("Failed to delete user.", "flash-error")
    return redirect(url_for('admin_users'))


# REPORTS
@app.route('/admin/reports', methods=['GET'])
@is_logged_in
@is_admin
def admin_reports():
    revenue_data = models.get_revenue_reports()
    grand_total = sum(float(row['total_revenue']) for row in revenue_data)
    return render_template('admin-reports.html', reports=revenue_data, grand_total=grand_total)

# ========== END OF ADMIN LOGIC ==========

# ========== START OF EVENTS LOGIC ==========

@app.route('/events')
def events():
    category_id = request.args.get('category_id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    is_free = request.args.get('is_free')

    public_events = models.get_public_events(category_id, start_date, end_date, is_free)
    categories = models.get_all_categories()

    return render_template('events.html', events=public_events, categories=categories)

@app.route("/events/<int:event_id>")
def event_details(event_id):
    event = models.get_event_by_id(event_id)
    if not event:
        flash("Event not found", "flash-error")
        return redirect(url_for('events'))
    
    tickets_left = event['capacity'] - event['tickets_sold']
    is_sold_out = tickets_left <= 0

    now = datetime.now()
    days_until_event = (event['start_date'] - now).days

    discount_multiplier = 1
    
    if days_until_event > 60:
        discount_multiplier = 0.8
    elif 50 < days_until_event <= 60:
        discount_multiplier = 0.8
    elif 35 < days_until_event <= 50:
        discount_multiplier = 0.85
    elif 25 < days_until_event <= 35:
        discount_multiplier = 0.9
    elif 15 < days_until_event <= 25:
        discount_multiplier = 0.95

    is_student = session.get('role') == 'student'

    return render_template("event-details.html", event=event, tickets_left=tickets_left, is_sold_out=is_sold_out, discount_multiplier=discount_multiplier, is_student=is_student) 

@app.route("/category/<name>")
def category(name):
    return f"Category page for {name}"

# ========== END OF EVENTS LOGIC ==========
