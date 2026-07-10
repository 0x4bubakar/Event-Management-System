import db_connector
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

def validate_event_dates(start_date, end_date, booking_deadline):
    try:
        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date)
        deadline_dt = datetime.fromisoformat(booking_deadline)

        if end_dt <= start_dt:
            return False, "The event's end date must be after its start date."
        
        if deadline_dt > start_dt:
            return False, "The booking deadline cannot be after the event has started."

        return True, ""
        
    except ValueError:
        return False, "Invalid date format submitted."
    
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

def get_event_status():
    conn = db_connector.get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        query = """
            SELECT 
                e.event_id, e.event_name, e.start_date, l.capacity,
                (SELECT COUNT(*) FROM booking b WHERE b.event_id = e.event_id AND b.status = 'confirmed') AS tickets_sold,
                (SELECT COUNT(*) FROM booking b WHERE b.event_id = e.event_id AND b.status = 'waitlisted') AS waitlisted
            FROM 
                event e
            JOIN 
                location l on e.location_id = l.location_id
            WHERE 
                e.start_date > NOW()
            ORDER BY 
                e.start_date ASC
        """
        cursor.execute(query)
        return cursor.fetchall()
    
    except Exception as e:
        print(f"Error fetching event statuses: {str(e)}")
        return []
    
    finally:
        cursor.close()

def get_applicable_discounts(event_id, days_until_event, is_student):
    conn = db_connector.get_connection()
    cursor = conn.cursor(dictionary=True)
    
    discounts_to_apply = []

    if days_until_event > 50 and days_until_event <= 60:
        discounts_to_apply.append("Early Bird 20")
    elif days_until_event > 35:
        discounts_to_apply.append("Early Bird 15")
    elif days_until_event > 25:
        discounts_to_apply.append("Early Bird 10")
    elif days_until_event > 15:
        discounts_to_apply.append("Early Bird 5")

    if is_student:
        discounts_to_apply.append("Student 10")
    
    applicable_discounts = []

    try:
        # discounts that aren't event-specific (event_id is null)
        for discount_name in discounts_to_apply:
            cursor.execute("SELECT discount_id, percent FROM discount WHERE name = %s and event_id IS NULL", (discount_name,)) # check the discounts exist in the discount table
            record = cursor.fetchone()
            if record:
                applicable_discounts.append({
                    "id": record['discount_id'],
                    "name": record['name'], 
                    "percent": float(record['percent'])/100.0
                    })
        
        # event-specific discounts
        cursor.execute("SELECT name, percent FROM discount WHERE event_id = %s", (event_id,))
        event_discounts = cursor.fetchall()

        for d in event_discounts:
            applicable_discounts.append({
                "id": d['discount_id'],
                "name": d['name'],
                "percent": float(d['percent'])/100.0
                })
        
        return applicable_discounts
    
    except Exception as e:
        print(f"Error fetching applicable discounts: {str(e)}")
        return []
    
    finally:
        cursor.close()


def create_event(location_id, category_id, organiser_id, event_name, start_date, end_date, conditions, booking_deadline, description, original_price, tickets):
    conn = db_connector.get_connection()
    cursor = conn.cursor()

    if organiser_id is None:
        status = "published"
    else:
        status = "draft"

    try:
        query = """
            INSERT INTO event(
                location_id, 
                category_id,
                organiser_id,
                event_name,
                start_date,
                end_date,
                conditions,
                booking_deadline,
                description,
                original_price,
                tickets,
                status)
            VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (location_id, category_id, organiser_id, event_name, start_date, end_date, conditions, booking_deadline, description, original_price, tickets, status))
        conn.commit()
        event_id = cursor.lastrowid
        return event_id
    
    except Exception as e:
        conn.rollback()
        print(f"Error creating event: {str(e)}")
        return None
    
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
        print(f"Error creating category: {str(e)}")
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
            SELECT
                e.*, c.category_name, l.name AS location_name, l.capacity,
                (SELECT COUNT(*) FROM booking b WHERE b.event_id = e.event_id AND b.status = 'confirmed') AS tickets_sold
            FROM 
                event e
            JOIN 
                category c ON e.category_id = c.category_id
            JOIN 
                location l ON e.location_id = l.location_id
            WHERE
                e.event_id = %s
        """
        cursor.execute(query, (event_id,))
        return cursor.fetchone()
    
    except Exception as e:
        print(f"Error fetching event details: {str(e)}")
        return None
    
    finally:
        cursor.close()

def get_public_events(category_id, start_date, end_date, is_free):
    conn = db_connector.get_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        query = """
            SELECT
                e.event_id, e.event_name, e.start_date, e.original_price, e.description, e.booking_deadline,
                c.category_name, l.name as location_name
            FROM 
                event e
            JOIN 
                category c ON e.category_id = c.category_id
            JOIN
                location l ON e.location_id = l.location_id
            WHERE 
                e.status = 'published'
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
            SELECT 
                e.*, l.name AS location_name
            FROM
                event e
            JOIN
                location l ON e.location_id = l.location_id
            WHERE
                e.start_date > NOW() AND e.status = 'published'
            ORDER BY
                e.start_date ASC
            LIMIT 4
        """    
        cursor.execute(query)
        return cursor.fetchall()
            
     except Exception as e:
         print(f"Error fetching latest four events: {str(e)}")
         return []
     
     finally:
         cursor.close()

def edit_events(location_id, category_id, organiser_id, event_name, start_date, end_date, conditions, booking_deadline, description, original_price, event_id, tickets):
    conn = db_connector.get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        set_clauses = [] # sql fragments
        params = [] # actual data values

        if location_id:
            set_clauses.append("location_id = %s")
            params.append(location_id)
        
        if category_id:
            set_clauses.append("category_id = %s")
            params.append(category_id)
        
        if organiser_id:
            set_clauses.append("organiser_id = %s")
            params.append(organiser_id)
        
        if event_name:
            set_clauses.append("event_name = %s")
            params.append(event_name)

        if start_date:
            set_clauses.append("start_date = %s")
            params.append(start_date)

        if end_date:
            set_clauses.append("end_date = %s")
            params.append(end_date)
        
        if conditions:
            set_clauses.append("conditions = %s")
            params.append(conditions)
        
        if booking_deadline:
            set_clauses.append("booking_deadline = %s")
            params.append(booking_deadline)

        if description:
            set_clauses.append("description = %s")
            params.append(description)
        
        if original_price:
            set_clauses.append("original_price = %s")
            params.append(original_price)

        if tickets:
            set_clauses.append("tickets = %s")
            params.append(tickets)
        
        if not set_clauses: # if nothing was actually edited, return false
            return False
        
        params.append(event_id)

        edit_query = "UPDATE event SET " + ", ".join(set_clauses) + " WHERE event_id = %s"
        
        cursor.execute(edit_query, tuple(params))
        conn.commit()
        return True
    
    except Exception as e:
        print(f"Error editing event: {e}")
        return False
    
    finally:
        cursor.close()

def is_location_suitable(location_id, category_id):
    conn = db_connector.get_connection()
    cursor = conn.cursor()

    try:
        query = "SELECT 1 FROM suitability WHERE location_id = %s and category_id = %s LIMIT 1"
        cursor.execute(query, (location_id, category_id))
        result = cursor.fetchall()
        return len(result) > 0
    
    except Exception as e:
        print(f"Suitability check error: {e}")
        return False
    
    finally:
        cursor.close()

def edit_location(name, capacity, address, suitabilities, location_id):
    conn = db_connector.get_connection()
    cursor = conn.cursor()

    try:
        set_clauses = [] # sql fragments
        params = [] # actual data values

        if name:
            set_clauses.append("name = %s")
            params.append(name)
        
        if capacity:
            set_clauses.append("capacity = %s")
            params.append(capacity)
        
        if address:
            set_clauses.append("address = %s")
            params.append(address)
        
        if set_clauses:
            params.append(location_id)
            edit_query = "UPDATE location SET " + ", ".join(set_clauses) + " WHERE location_id = %s"
            cursor.execute(edit_query, (tuple(params)))

        if suitabilities is not None:
            # Clear all previous category suitability links
            cursor.execute("DELETE FROM suitability WHERE location_id = %s", (location_id,))
            # Insert new category links
            suit_query = "INSERT INTO suitability (location_id, category_id) VALUES (%s, %s)"
            for category_id in suitabilities:
                cursor.execute(suit_query, (location_id, category_id))

        conn.commit()
        return True
    
    except Exception as e:
        conn.rollback()
        print(f"Error editing location: {str(e)}")
        return False
    
    finally:
        cursor.close()

def get_location_by_id(location_id):
    conn = db_connector.get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM location WHERE location_id = %s", (location_id,))
        return cursor.fetchone()
    except Exception as e:
        print(f"Error fetching location: {e}")
        return None
    finally:
        cursor.close()