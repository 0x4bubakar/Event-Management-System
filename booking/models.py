import db_connector
from datetime import datetime
from users.models import get_user_by_id

def create_booking(user_id, event_id, days_booked, attendee_name):
    conn = db_connector.get_connection()
    cursor = conn.cursor(dictionary=True)

    user_data = get_user_by_id(user_id)
    now = datetime.now()

    if not user_data:
        return False, "Please sign in before booking."

    is_student = user_data and user_data['role'] == 'student'
    

    if not isinstance(days_booked, int) or days_booked <= 0:
        return False, "Number of days booked can only be a positive whole number."
    
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
        
        if not event:
            return False, "Event doesn't exist."
        
        event_length = (event['end_date'].date() - event['start_date'].date()).days + 1 # ensure that the difference between 2 dates (ie Fri 1st to Sun 3rd) doesnt subtract the first day of the event, and that one-day events are handled correctly.
        
        if days_booked > event_length:
            return False, "Tickets can only be booked for the duration of the event."

        if now > event['booking_deadline']:
            return False, "The booking deadline has passed."
        
        if event['tickets_sold'] >= event['capacity']:
            status = "waitlisted"
        else:
            status = 'confirmed'
        
        base_price_per_day = float(event['original_price']) / event_length
        booked_base_price = base_price_per_day * days_booked

        insert_query = """
            INSERT INTO booking (user_id, event_id, booked_on, status, booked_base_price, days_booked, attendee_name)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (user_id, event_id, now, status, booked_base_price, days_booked, attendee_name))
        booking_id = cursor.lastrowid
        
        days_until_event = (event['start_date'] - now).days
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
        
        current_price = booked_base_price

        # standard discounts
        for discount in discounts_to_apply: 
            cursor.execute("SELECT discount_id, percent FROM discount WHERE name = %s and event_id IS NULL", (discount,)) # check the discounts exist in the discount table
            discount_record = cursor.fetchone()

            if discount_record:
                percent_decimal = float(discount_record['percent']) / 100.0
                amount_deducted = current_price * percent_decimal

                cursor.execute("""
                    INSERT INTO booking_discounts (booking_id, discount_id, amount_deducted)
                    VALUES (%s, %s, %s)
                """, (booking_id, discount_record['discount_id'], amount_deducted))

                current_price -= amount_deducted
        

        # event-specific discounts
        cursor.execute("SELECT discount_id, percent FROM discount WHERE event_id=%s", (event_id,))
        event_specific_discounts = cursor.fetchall()

        if event_specific_discounts:
            for discount in event_specific_discounts:
                percent_decimal = float(discount['percent']) / 100.0
                amount_deducted = current_price * percent_decimal

                cursor.execute("""
                    INSERT INTO booking_discounts (booking_id, discount_id, amount_deducted)
                    VALUES (%s, %s, %s)
                """, (booking_id, discount['discount_id'], amount_deducted))

                current_price -= amount_deducted
        
        conn.commit()
        
        if status == 'waitlisted':
            message = f"Booking confirmed! You have been added to the waiting list. (Price locked at £{current_price:.2f})"
        else:
            message = f"Booking confirmed! You paid £{current_price:.2f}"

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
            SELECT 
                b.event_id, 
                e.start_date,
                b.status,
                (b.booked_base_price - COALESCE(SUM(bd.amount_deducted), 0)) AS final_price
            FROM
                booking b
            JOIN
                event e ON b.event_id = e.event_id
            LEFT JOIN
                booking_discounts bd ON b.booking_id = bd.booking_id
            WHERE
                b.booking_id = %s AND b.user_id = %s AND b.status != 'cancelled'
            GROUP BY
                b.booking_id,
                b.event_id,
                e.start_date,
                b.booked_base_price
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

        cancel_booking_query = "UPDATE booking SET status = 'cancelled' WHERE booking_id = %s"
        cursor.execute(cancel_booking_query, (booking_id,))

        insert_cancel_query = """
            INSERT INTO cancel (booking_id, cancellation_fee, cancelled_on)
            VALUES (%s, %s, %s)
        """

        cursor.execute(insert_cancel_query, (booking_id, penalty_amount, now))

        # waitlist management - giving a space to the next person in the queue
        if booking['status'] == "confirmed": # only promote a waitlisted user if a free space was actually opened after cancellation
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