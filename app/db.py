from werkzeug.security import generate_password_hash, check_password_hash

def create_user(username, plain_text_password):
    hashed_password = generate_password_hash(plain_text_password)

def verify_login(username, provided_password):

    return check_password_hash(db_hashed_pw, provided_password)