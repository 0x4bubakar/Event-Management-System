import db_connector
from datetime import datetime
from users.models import get_user_by_id

def create_booking(user_id, event_id, days_booked):
    conn = db_connector.get_connection()
    cursor = conn.cursor(dictionary=True)

    user_data = get_user_by_id(user_id)
    is_student = user_data and user_data['role'] == 'student'
    now = datetime.now()

    if not (isinstance(days_booked, int)):
        return False, "Number of days booked can only be whole numbers."
    else:
        if days_booked <= 0:
            return False, "You can only book a positive number of days."

    try:
        query = """
            SELECT e.original_price, e.start_date, e.end_date, e.booking_deadline, l.capacity,
            (SELECT COUNT(*) FROM booking b WHERE b.event_id = e.event_id AND b.status='confirmed') AS tickets_sold
            FROM event e
            JOIN location l on e.location_id = l.location_id
            WHERE e.event_id = %s
        """

        cursor.execute(query, (event_id,))
        event = cursor.fetchone()
        event_length = (event['end_date'].date() - event['start_date'].date()).days

        if days_booked > event_length:
            return False, "Tickets can only be booked for the duration of the event."
        
        if not event:
            return False, "Event doesn't exist."
        

        if now > event['booking_deadline']:
            return False, "The booking deadline has passed."
        


        base_price_per_day = float(event['original_price']) / event_length
        final_price = base_price_per_day * days_booked

        days_until_event = (event['start_date'] - now).days
    
        if days_until_event > 60:
            final_price = final_price * 0.8
        if days_until_event > 50  and days_until_event <= 60:
            final_price = final_price * 0.8
        elif days_until_event > 35 and days_until_event <= 50:
            final_price = final_price * 0.85
        elif days_until_event > 25 and days_until_event <= 35:
            final_price = final_price * 0.9
        elif days_until_event > 15 and days_until_event <= 25:
            final_price = final_price * 0.95

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