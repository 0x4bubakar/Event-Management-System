import db_connector
from werkzeug.security import generate_password_hash, check_password_hash

# admin update/delete funcs to be replaced with the regular ones

def get_all_events_admin():
    conn = db_connector.get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        query = """
            SELECT e.event_id, e.event_name, e.start_date, e.original_price,
            c.category_name, l.name as location_name
            FROM event e
            JOIN category c ON e.category_id = c.category_id
            JOIN location l ON e.location_id = l.location_id
            ORDER BY e.start_date
        """

        cursor.execute(query)
        return cursor.fetchall()
    
    except Exception as e:
        print(f"Error with fetching events: {str(e)}")
        return []
    
    finally:
        cursor.close()



def admin_update_password(target_user_id, new_password):
    conn = db_connector.get_connection()
    cursor = conn.cursor()

    try:
        hashed_pw = generate_password_hash(new_password)
        query = "UPDATE user SET password_hash = %s WHERE user_id = %s"
        cursor.execute(query, (hashed_pw, target_user_id))
        conn.commit()
        return True
    
    except Exception as e:
        conn.rollback()
        return False
    
    finally:
        cursor.close()

def get_all_users():
    conn = db_connector.get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT user_id, name, email, role FROM user")
    users = cursor.fetchall()
    cursor.close()
    return users

def admin_update_password(target_user_id, new_password):
    conn = db_connector.get_connection()
    cursor = conn.cursor()

    try:
        hashed_pw = generate_password_hash(new_password)
        query = "UPDATE user SET password_hash = %s WHERE user_id = %s"
        cursor.execute(query, (hashed_pw, target_user_id))
        conn.commit()
        return True
    
    except Exception as e:
        conn.rollback()
        return False
    
    finally:
        cursor.close()

def admin_delete_account(target_user_id):
    conn = db_connector.get_connection()
    cursor = conn.cursor()

    try:
        query = "DELETE FROM user WHERE user_id = %s"
        cursor.execute(query, (target_user_id,))
        conn.commit()
        return True
    
    except Exception as e:
        conn.rollback()
        return False
    
    finally:
        cursor.close()