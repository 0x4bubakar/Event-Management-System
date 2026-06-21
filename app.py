from . import db_connector
from flask import Flask
from dotenv import load_dotenv

load_dotenv()
app.secret_key = os.getenv("SECRET_KEY")
app = Flask(__name__)
  
import auth
import admin
import organisers
import events
import main
from error import handler
import users