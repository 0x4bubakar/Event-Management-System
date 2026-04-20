import os
from app import app, models
from flask import Flask, redirect, render_template, url_for, request, flash, session
from dotenv import load_dotenv
load_dotenv()

app.secret_key = os.getenv("SECRET_KEY")

@app.route('/')
def index():
    if session.get("user_id"):
        return redirect(url_for('events'))
    else:
        return render_template('index.html')

@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404


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
                return redirect(url_for('index'))
            else:
                flash(message, "flash-error")
        else:
            flash("One of the fields are missing information. Please fill them in.", "flash-error")
    return render_template('login.html')


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