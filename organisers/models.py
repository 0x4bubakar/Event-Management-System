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
    cursor = conn.cursor(dictionary=True)

    query = "SELECT organiser_id, description FROM organiser WHERE user_id=%s"
    
    try:
        cursor.execute(query, (user_id,))
        org_data = cursor.fetchone()
        return org_data
    except Exception as e:
        print(f"Error fetching organiser_id from user_id: {str(e)}")
        return None
    finally:
        cursor.close()

def edit_org_profile(org_id,  description):
    conn = db_connector()
    cursor = conn.cursor()
    try:
        edit_query = "UPDATE organiser SET description = %s WHERE organiser_id = %s"
        cursor.execute(edit_query, (description, org_id))
        conn.commit()
        return True
    
    except Exception as e:
        conn.rollback()
        print(f"Error editing organiser profile: {e}")
        return False
    
    finally:
        cursor.close()

def get_all_events_org(org_id):
    conn = db_connector.get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        query = """
            SELECT e.event_id, e.event_name, e.start_date, e.original_price, e.tickets, e.status,
            c.category_name, l.name as location_name, l.capacity,
            (SELECT COUNT(*) FROM booking b WHERE b.event_id = e.event_id AND b.status = 'confirmed') AS tickets_sold
            FROM event e
            JOIN category c ON e.category_id = c.category_id
            JOIN location l ON e.location_id = l.location_id
            WHERE e.organiser_id = %s
        """

        cursor.execute(query, (org_id,))
        return cursor.fetchall()
    
    except Exception as e:
        print(f"Error with fetching events: {str(e)}")
        return []
    
    finally:
        cursor.close()

def publish_draft_event(event_id):
    conn = db_connector.get_connection()
    cursor = conn.cursor()

    try:
        publish_query = "UPDATE event SET status = 'published' WHERE event_id = %s"
        cursor.execute(publish_query, (event_id,))
        conn.commit()
        return True
    
    except Exception as e:
        print(f"Error publishing event: {e}")
        return False
    
    finally:
        cursor.close()