from werkzeug.security import generate_password_hash, check_password_hash
from app import db

def create_user(name, email, plain_text_password):
    if name != None and email != None and plain_text_password != None: 
        cursor = db.get_connection().cursor()
        query = "SELECT email from user WHERE email = %s"
        cursor.execute(query, email)
        user_exists = cursor.fetchone()
        if user_exists:
            error = "Account already exists, please log in."
            return False, error
        else:
            #query = "SELECT"
            hashed_password = generate_password_hash(plain_text_password)




    

def verify_login(email, provided_password):
    cursor = db.get_connection().cursor()
    query = "SELECT password_hash FROM user WHERE email = %s"
    cursor.execute(query, email)
    db_hashed_pw = cursor.fetchone()
    cursor.close()
    return check_password_hash(db_hashed_pw, provided_password)