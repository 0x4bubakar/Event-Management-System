import db_connector
from werkzeug.security import generate_password_hash, check_password_hash

def get_quick_stats():
    conn = db_connector.get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        query = """ # calculate total revenue by summing the cancellation fees and confirmed ticket's base prices, subtracting the discounts 
            SELECT
                (SELECT COUNT(*) FROM event WHERE status = 'published') AS total_events,
                (SELECT COUNT(*) FROM booking WHERE status = 'confirmed') AS total_bookings,
                (SELECT COUNT(*) FROM user WHERE role = 'user' OR role = 'student') AS total_users,
                (
                    (SELECT COALESCE(SUM(booked_base_price), 0)
                    FROM booking
                    WHERE status = 'confirmed')

                    -

                    (SELECT COALESCE(SUM(bd.amount_deducted), 0)
                    FROM booking_discounts bd
                    JOIN booking b ON bd.booking_id = b.booking_id
                    WHERE b.status = 'confirmed')

                    +

                    (SELECT COALESCE(SUM(cancellation_fee), 0)
                    FROM cancel)

                ) AS total_revenue
        """

        cursor.execute(query)
        stats = cursor.fetchone()
        return stats
    
    except Exception as e:
        print(f"Error fetching quick stats for admin dashboard homepage: {str(e)}")
        return {
            "total_events": -1,
            "total_bookings": -1,
            "total_users": -1,
            "total_revenue": 0.00
        }
    
    finally:
        cursor.close()

def get_all_events_admin():
    conn = db_connector.get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        query = """
            SELECT e.event_id, e.event_name, e.start_date, e.original_price, e.status,
            c.category_name, l.name as location_name, l.capacity,
            (SELECT COUNT(*) FROM booking b WHERE b.event_id = e.event_id AND b.status = 'confirmed') AS tickets_sold
            FROM event e
            JOIN category c ON e.category_id = c.category_id
            JOIN location l ON e.location_id = l.location_id
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
        print(f"Error updating user {target_user_id}'s password: {str(e)}")
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

def db_delete_category(cat_id):
    conn = db_connector.get_connection()
    cursor = conn.cursor()

    try:
        query = "DELETE FROM category WHERE category_id = %s"
        cursor.execute(query, (cat_id,))
        conn.commit()
        return True
    
    except Exception as e:
        conn.rollback()
        print(f"Error deleting category: {str(e)}")
        return False
    
    finally:
        cursor.close()