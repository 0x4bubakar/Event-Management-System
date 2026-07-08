import db_connector
from werkzeug.security import generate_password_hash, check_password_hash

def create_organiser(name, email, password):
    conn = db_connector.get_connection()
    cursor = conn.cursor()

    query = "SELECT email from user WHERE email = %s"
    cursor.execute(query, (email,))
    user_exists = cursor.fetchone()
    
    if user_exists:
        return None, None, "Account already exists, please log in."
    
    else:
        user_query = "INSERT INTO user (name, email, password_hash, role) VALUES(%s, %s, %s, %s)"
        org_query = "INSERT INTO organiser (user_id) VALUES(%s)"
        password_hash = generate_password_hash(password)
        role = "organiser"
        
        try:
            cursor.execute(user_query, (name, email, password_hash, role))
            user_id = cursor.lastrowid
            cursor.execute(org_query, (user_id,))
            conn.commit()
            return user_id, role, "Organiser created successfully!"
        
        except Exception as e:
            conn.rollback()
            print(f"Database error: {str(e)}")
            return None, None, "System error, please try again later."
        
        finally:
            cursor.close()

def get_org_by_user_id(user_id):
    conn = db_connector.get_connection()
    cursor = conn.cursor()

    query = "SELECT organiser_id FROM organiser WHERE user_id=%s"
    
    try:
        org_id = cursor.execute(query, (user_id,))
        if org_id:
            return org_id
        else:
            return None
    except Exception as e:
        print(f"Error fetching organiser_id from user_id: {str(e)}")
        return None
    finally:
        cursor.close()