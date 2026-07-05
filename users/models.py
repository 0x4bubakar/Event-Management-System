import db_connector
from werkzeug.security import generate_password_hash, check_password_hash

def get_user_by_id(user_id):
    conn = db_connector.get_connection()
    cursor = conn.cursor()

    try:
        query = "SELECT name, email, role FROM user WHERE user_id = %s"
        cursor.execute(query, (user_id,))
        user_record = cursor.fetchone()
        if user_record:
            return {
                "name": user_record[0],
                "email": user_record[1],
                "role": user_record[2]
            }
        return None
    
    except Exception as e:
        print(f"Database error: {str(e)}")
        return None
    
    finally:
        cursor.close()

def create_user(name, email, plain_text_password):
    conn = db_connector.get_connection()
    cursor = conn.cursor()

    query = "SELECT email from user WHERE email = %s"
    cursor.execute(query, (email,))
    user_exists = cursor.fetchone()
    
    if user_exists:
        return None, None, "Account already exists, please log in."
    
    else:
        query = "INSERT INTO user (name, email, password_hash, role) VALUES(%s, %s, %s, %s)"
        password_hash = generate_password_hash(plain_text_password)

        default_role = "student" if email.lower().endswith(".ac.uk") else "member"

        try:
            cursor.execute(query, (name, email, password_hash, default_role))
            conn.commit()
            user_id = cursor.lastrowid
            
            return user_id, default_role, "User created successfully!"
        
        except Exception as e:
            conn.rollback()
            print(f"Database error: {str(e)}")
            return None, None, "System error, please try again later."
        
        finally:
            cursor.close()

def update_user(user_id, name, email, password):
    conn = db_connector.get_connection()
    cursor = conn.cursor()
    default_role = "student" if email.lower().endswith(".ac.uk") else "member"

    try:
        if password:
            hashed_password = generate_password_hash(password)
            query = "UPDATE user SET name = %s, email = %s, password_hash = %s, role = %s WHERE user_id = %s"
            cursor.execute(query, (name, email, hashed_password, default_role, user_id, ))
        
        else:
            query = "UPDATE user SET name = %s, email = %s, role=%s WHERE user_id = %s"
            cursor.execute(query, (name, email, default_role, user_id ))

        conn.commit()
        return True
    
    except Exception as e:
        conn.rollback()
        print(f"Account details update error: {str(e)}")
        return False
    
    finally:
        cursor.close()

def delete_account(target_user_id):
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

def get_bookings_by_id(user_id):
    conn = db_connector.get_connection()
    cursor = conn.cursor()

    try:
        query = """
        SELECT 
            event.event_name, 
            event.start_date, 
            booking.days_booked, 
            booking.status, 
            (booking.booked_base_price - COALESCE(SUM(booking_discounts.amount_deducted),0)) as final_price, 
            booking.booking_id 
        FROM 
            booking 
        JOIN 
            event ON booking.event_id = event.event_id 
        LEFT JOIN 
            booking_discounts ON booking.booking_id = booking_discounts.booking_id
        WHERE 
            booking.user_id = %s
        GROUP BY
            booking.booking_id,
            event.event_name,
            event.start_date,
            booking.days_booked,
            booking.status,
            booking.booked_base_price
        """
        cursor.execute(query, (user_id,))
        records = cursor.fetchall()

        bookingsList = []

        for row in records:
            bookingsList.append({
                "event_name": row[0],
                "start_date": row[1],
                "days_booked": row[2],
                "booking_status": row[3],
                "final_price": float(row[4]),
                "booking_id": row[5]
            })

        return bookingsList
    
    except Exception as e:
        print(f"Database error in bookings: {str(e)}")
        return []
    
    finally:
        cursor.close()
