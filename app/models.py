from werkzeug.security import generate_password_hash, check_password_hash
from app import db

def create_user(email, plain_text_password):
    db.get_connection().cursor()
    hashed_password = generate_password_hash(plain_text_password)
    

def verify_login(email, provided_password):
    cursor = db.get_connection().cursor()
    query = "SELECT password_hash FROM user WHERE email = %s"
    cursor.execute(query, email)
    db_hashed_pw = cursor.fetchone()
    cursor.close()
    return check_password_hash(db_hashed_pw, provided_password)