import os
from app import app, routes
from flask import Flask, redirect, render_template, url_for, request
from dotenv import load_dotenv
load_dotenv()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        record = db.verify_login(email, password)
    return render_template('login.html')

# some route for registration

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