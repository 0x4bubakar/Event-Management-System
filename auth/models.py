from werkzeug.security import generate_password_hash, check_password_hash
import db_connector

def verify_login(email, provided_password):
    conn = db_connector.get_connection()
    cursor = conn.cursor()
    
    try:
        query = "SELECT password_hash, user_id, name, role FROM user WHERE email = %s"
        cursor.execute(query, (email,))
        user_record = cursor.fetchone()

        if user_record:
            db_hashed_pw = user_record[0]
            user_id = user_record[1] 
            name = user_record[2]  
            role = user_record[3]    
            if check_password_hash(db_hashed_pw, provided_password):
                return user_id, name, role, "Successfully logged in!"
            else:
                return None, None, None, "Invalid credentials, please try again"
        else:
            return None, None, None, "Invalid credentials, please try again"

    except Exception as e:
        print(f"Database error: {str(e)}")
        return None, "System error, please try again later."
    
    finally:
        cursor.close()