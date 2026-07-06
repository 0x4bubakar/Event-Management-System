import os
import db_connector
from flask import Flask
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
  
from admin.routes import admin_bp
from auth.routes import auth_bp
from booking.routes import booking_bp
from error.handler import error_bp
from events.routes import events_bp
from main.routes import main_bp
from organisers.routes import organisers_bp
from reports.routes import reports_bp
from users.routes import users_bp
from invoices.routes import invoices_bp

app.register_blueprint(admin_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(booking_bp)
app.register_blueprint(error_bp)
app.register_blueprint(events_bp)
app.register_blueprint(main_bp)
app.register_blueprint(organisers_bp)
app.register_blueprint(reports_bp)
app.register_blueprint(users_bp)
app.register_blueprint(invoices_bp)