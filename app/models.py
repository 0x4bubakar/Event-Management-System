from werkzeug.security import generate_password_hash, check_password_hash
from app import db

def create_user(name, email, plain_text_password):
    conn = db.get_connection()
    cursor = conn.cursor()

    query = "SELECT email from user WHERE email = %s"
    cursor.execute(query, (email,))
    user_exists = cursor.fetchone()
    
    if user_exists:
        return None, "Account already exists, please log in."
    
    else:
        query = "INSERT INTO user (name, email, password_hash, role) VALUES(%s, %s, %s, %s)"
        password_hash = generate_password_hash(plain_text_password)
        default_role = "member";
        try:
            cursor.execute(query, (name, email, password_hash, default_role))
            conn.commit()
            user_id = cursor.lastrowid
            return user_id, "User created successfully!"
        
        except Exception as e:
            conn.rollback()
            print(f"Database error: {str(e)}")
            return None, "System error, please try again later."
        
        finally:
            cursor.close()

def verify_login(email, provided_password):
    conn = db.get_connection()
    cursor = conn.cursor()
    
    try:
        query = "SELECT password_hash, user_id, name FROM user WHERE email = %s"
        cursor.execute(query, (email,))
        user_record = cursor.fetchone()

        if user_record:
            db_hashed_pw = user_record[0]
            user_id = user_record[1] 
            name = user_record[2]      
            if check_password_hash(db_hashed_pw, provided_password):
                return user_id, name, "Successfully logged in!"
            else:
                return None, None, "Invalid credentials, please try again"
        else:
            return None, None, "Invalid credentials, please try again"

    except Exception as e:
        print(f"Database error: {str(e)}")
        return None, "System error, please try again later."
    
    finally:
        cursor.close()