from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import db_connector

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
        query = "SELECT event.event_name, event.start_date, booking.days_booked, booking.status, booking.final_price, booking.booking_id FROM booking JOIN event ON booking.event_id = event.event_id WHERE booking.user_id = %s"
        cursor.execute(query, (user_id,))
        records = cursor.fetchall()

        bookingsList = []

        for row in records:
            bookingsList.append({
                "event_name": row[0],
                "start_date": row[1],
                "days_booked": row[2],
                "booking_status": row[3],
                "final_price": row[4],
                "booking_id": row[5]
            })

        return bookingsList
    
    except Exception as e:
        print(f"Database error in bookings: {str(e)}")
        return []
    
    finally:
        cursor.close()
        

def get_all_locations():
    conn = db_connector.get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT location_id, name, capacity FROM location")
    locations = cursor.fetchall()
    cursor.close()
    
    return locations

def get_all_categories():
    conn = db_connector.get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT category_id, category_name FROM category")
    categories = cursor.fetchall()
    cursor.close()
    
    return categories

def get_all_suitabilities():
    conn = db_connector.get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT location_id, category_id FROM suitability")
    mapping = cursor.fetchall()
    cursor.close()
    conn.close()
    return mapping


def get_current_event_statuses():
    conn = db_connector.get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        query = """
            SELECT e.event_id, e.event_name, e.start_date, l.capacity,
            (SELECT COUNT(*) FROM booking b WHERE b.event_id = e.event_id AND b.status != 'cancelled') AS tickets_sold
            FROM event e
            JOIN location l on e.location_id = l.location_id
            WHERE e.start_date > NOW()
            ORDER BY e.start_date ASC
        """
        cursor.execute(query)
        return cursor.fetchall()
    
    except Exception as e:
        print(f"Error fetching event statuses: {str(e)}")
        return []
    
    finally:
        cursor.close()


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

def get_revenue_reports():
    conn = db_connector.get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        query = """
            SELECT e.event_id, e.event_name, e.start_date,
            COUNT(b.booking_id) AS total_bookings,
            COALESCE(SUM(b.final_price), 0) AS total_revenue
            FROM event e
            LEFT JOIN booking b ON event.event_id = b.event_id AND b.status != 'cancelled'
            GROUP BY e.event_id, e.event_name, e.start_date
            ORDER BY e.start_date DESC
        """
        cursor.execute(query)
        return cursor.fetchall()
    
    except Exception as e:
        print(f"Error generating reports: {str(e)}")
        return []
    
    finally:
        cursor.close()

def delete_event(event_id):
    conn = db_connector.get_connection()
    cursor = conn.cursor()

    try:
        query = "DELETE FROM event WHERE event_id = %s"
        cursor.execute(query, (event_id,))
        conn.commit()
        return True
    
    except Exception as e:
        print(f"Error with deleting event: {str(e)}")
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

def create_event(location_id, event_name, start_date, end_date, conditions, booking_deadline, description, category_id, original_price):
    conn = db_connector.get_connection()
    cursor = conn.cursor()

    try:
        query = """
            INSERT INTO event
            (location_id, event_name, start_date, end_date, conditions, booking_deadline, description, category_id, original_price, discount_rate)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 0.00)
        """
        cursor.execute(query, (location_id, event_name, start_date, end_date, conditions, booking_deadline, description, category_id, original_price))
        conn.commit()
        
        return True
    
    except Exception as e:
        conn.rollback()
        print(f"Error creating event: {str(e)}")
        return False
    
    finally:
        cursor.close()

def create_category(category_name):
    conn = db_connector.get_connection()
    cursor = conn.cursor()

    try:
        query = "INSERT INTO category (category_name) VALUES (%s)"
        cursor.execute(query, (category_name,))
        conn.commit()
        return True
    
    except Exception as e:
        conn.rollback()
        print(f"Error creating event: {str(e)}")
        return False
    
    finally:
        cursor.close()


def create_location(name, capacity, address, suitabilities):
    conn = db_connector.get_connection()
    cursor = conn.cursor()

    try:
        query = "INSERT INTO location (name, capacity, address) VALUES (%s, %s, %s)"
        cursor.execute(query, (name, capacity, address))

        new_location_id = cursor.lastrowid
        
        if suitabilities:
            suit_query = "INSERT INTO suitability (location_id, category_id) VALUES (%s, %s)"
            for category_id in suitabilities:
                cursor.execute(suit_query, (new_location_id, category_id))

        conn.commit()
        return True
    
    except Exception as e:
        conn.rollback()
        print(f"Error creating location: {str(e)}")
        return False
    
    finally:
        cursor.close()

def get_event_by_id(event_id):
    conn = db_connector.get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        query = """
            SELECT e.*, c.category_name, l.name AS location_name, l.capacity,
            (SELECT COUNT(*) FROM booking b WHERE b.event_id = e.event_id AND b.status != 'cancelled') AS tickets_sold
            FROM event e
            JOIN category c ON e.category_id = c.category_id
            JOIN location l ON e.location_id = l.location_id
            WHERE e.event_id = %s
        """
        cursor.execute(query, (event_id,))
        return cursor.fetchone()
    
    except Exception as e:
        print(f"Error fetching event details: {str(e)}")
        return None
    
    finally:
        cursor.close()

def get_public_events(category_id=None, start_date=None, end_date=None, is_free=None):
    conn = db_connector.get_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        query = """
            SELECT e.event_id, e.event_name, e.start_date, e.original_price, e.description,
                   c.category_name, l.name as location_name
            FROM event e
            JOIN category c ON e.category_id = c.category_id
            JOIN location l ON e.location_id = l.location_id
            WHERE e.start_date > NOW()
        """
        params = []

        if category_id:
            query += " AND e.category_id = %s"
            params.append(category_id)
            
        if start_date:
            query += " AND e.start_date >= %s"
            params.append(start_date)
            
        if end_date:
            query += " AND e.start_date <= %s"
            params.append(end_date + " 23:59:59")
            
        if is_free:
            query += " AND e.original_price = 0"

        query += " ORDER BY e.start_date ASC"

        cursor.execute(query, tuple(params))
        return cursor.fetchall()
        
    except Exception as e:
        print(f"Error fetching filtered events: {str(e)}")
        return []
    finally:
        cursor.close()

def fetch_recent_events():
     conn = db_connector.get_connection()
     cursor = conn.cursor(dictionary=True)

     try:
        query = """
            SELECT e.*, l.name AS location_name
            FROM event e
            JOIN location l ON e.location_id = l.location_id
            WHERE e.start_date > NOW()
            ORDER BY e.start_date ASC
            LIMIT 4
        """    
        cursor.execute(query)
        return cursor.fetchall()
            
     except Exception as e:
         print(f"Error fetching latest four events: {str(e)}")
         return []
     
     finally:
         cursor.close()

def create_booking(user_id, event_id, days_booked):
    conn = db_connector.get_connection()
    cursor = conn.cursor(dictionary=True)

    user_data = get_user_by_id(user_id)
    is_student = user_data and user_data['role'] == 'student'

    try:
        query = """
            SELECT e.original_price, e.start_date, e.booking_deadline, l.capacity,
            (SELECT COUNT(*) FROM booking b WHERE b.event_id = e.event_id AND b.status='confirmed') AS tickets_sold
            FROM event e
            JOIN location l on e.location_id = l.location_id
            WHERE e.event_id = %s
        """

        cursor.execute(query, (event_id,))
        event = cursor.fetchone()

        if not event:
            return False, "Event doesn't exist."
        
        now = datetime.now()

        if now.date() > event['booking_deadline']:
            return False, "The booking deadline has passed."
        

        days_booked = int(days_booked)
        base_price = float(event['original_price']) * days_booked
        final_price = base_price

        days_until_event = (event['start_date'] - now).days
    
        if days_until_event > 60:
            final_price = base_price * 0.8
        if days_until_event > 50  and days_until_event <= 60:
            final_price = base_price * 0.8
        elif days_until_event > 35 and days_until_event <= 50:
            final_price = base_price * 0.85
        elif days_until_event > 25 and days_until_event <= 35:
            final_price = base_price * 0.9
        elif days_until_event > 15 and days_until_event <= 25:
            final_price = base_price * 0.95

        if is_student:
            final_price = final_price * 0.90

        if event['tickets_sold'] >= event['capacity']:
            status = 'waitlisted'
            message = f"Booking confirmed! You have been added to the waiting list. (Price locked at £{final_price:.2f})"

        else:
            status = 'confirmed'
            message = f"Booking confirmed! You paid £{final_price:.2f}"

        insert_query = """
            INSERT INTO booking (user_id, event_id, booked_on, status, final_price, days_booked)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (user_id, event_id, now, status, final_price, days_booked))
        conn.commit()
        
        return True, message
    
    except Exception as e:
        conn.rollback()
        print(f"Booking error: {str(e)}")
        return False, "System error while booking. Please try again later."
    
    finally:
        cursor.close()

def cancel_booking(booking_id, user_id):
    conn = db_connector.get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        query = """
            SELECT b.final_price, b.event_id, e.start_date 
            FROM booking b
            JOIN event e ON b.event_id = e.event_id
            WHERE b.booking_id = %s AND b.user_id = %s AND b.status != 'cancelled'
        """
        cursor.execute(query, (booking_id, user_id))
        booking = cursor.fetchone()

        if not booking:
            return False, "Booking not found or already cancelled."

        now = datetime.now()
        days_until_event = (booking['start_date'] - now).days
        original_paid = float(booking['final_price'])

        if days_until_event >= 40:
            penalty_rate = 0.0     # 0% charge
        elif 25 <= days_until_event <= 39:
            penalty_rate = 0.40    # 40% charge
        else:
            penalty_rate = 1.0     # 100% charge

        penalty_amount = original_paid * penalty_rate
        refund_amount = original_paid - penalty_amount

        cancel_query = "UPDATE booking SET status = 'cancelled' WHERE booking_id = %s"
        cursor.execute(cancel_query, (booking_id,))

        waitlist_query = """
            SELECT booking_id FROM booking 
            WHERE event_id = %s AND status = 'waitlisted' 
            ORDER BY booked_on ASC LIMIT 1
        """
        cursor.execute(waitlist_query, (booking['event_id'],))
        next_in_line = cursor.fetchone()

        if next_in_line:
            promote_query = "UPDATE booking SET status = 'confirmed' WHERE booking_id = %s"
            cursor.execute(promote_query, (next_in_line['booking_id'],))

        conn.commit()

        message = f"Booking cancelled. Penalty Fee: £{penalty_amount:.2f}. Total Refund: £{refund_amount:.2f}."
        return True, message

    except Exception as e:
        conn.rollback()
        print(f"Cancel booking error: {str(e)}")
        return False, "System error while cancelling. Please try again."

    finally:
        cursor.close()