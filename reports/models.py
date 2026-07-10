import db_connector
from datetime import datetime
from reportlab import *

def get_monthly_revenue_for_year(year):
    conn = db_connector.get_connection()
    cursor = conn.cursor(dictionary=True)

    # init each month with zeroed data
    monthly_data = {
        month: {
            "ticket_revenue": 0.0,
            "cancellation_fees": 0.0,
            "hosting_fees": 0.0,
            "total": 0.0,
        } for month in range (1, 13)
    }

    try:
        # calculate ticket sales revenue per month
        ticket_query = """
            SELECT
                MONTH(b.booked_on) as month,
                b.booked_base_price,
                COALESCE((SELECT SUM(amount_deducted) FROM booking_discounts bd WHERE bd.booking_id = b.booking_id), 0) as discount
            FROM
                booking b
            WHERE
                b.status = 'confirmed' AND YEAR(b.booked_on) = %s
        """

        cursor.execute(ticket_query, (year,))

        for row in cursor.fetchall():
            m = row['month']
            revenue = float(row['booked_base_price']) - float(row['discount'])
            monthly_data[m]['ticket_revenue'] += revenue

        # calculate extra revenue from ticket cancellation fees
        cancel_query = """
            SELECT MONTH(c.cancelled_on) as month, c.cancellation_fee
            FROM cancel
            WHERE YEAR(c.cancelled_on) = %s
        """

        cursor.execute(cancel_query, (year,))

        for row in cursor.fetchall():
            monthly_data[row['month']]['cancellation_fees'] += float(row['cancellation_fee'])

        # calculate extra revenue from hosting fees
        fee_query = """
            SELECT MONTH(start_date) as month, COUNT(*) as event_count
            FROM event
            WHERE organiser_id IS NOT NULL AND status = 'published' AND YEAR(start_date) = %s
            GROUP BY MONTH(start_date)
        """

        cursor.execute(fee_query, (year,))

        for row in cursor.fetchall():
            m = row['month']
            monthly_data[m]['hosting_fees'] += row['event_count'] * 100.0
            
        # calculate totals
        for m in monthly_data:
            monthly_data[m]['total'] = monthly_data[m]['ticket_revenue'] + monthly_data[m]['cancellation_fees'] + monthly_data[m]['hosting_fees']
        
        return monthly_data
    
    except Exception as e:
        print(f"Error fetching monthly monthly revenue: {e}")
        return monthly_data
    
    finally:
        cursor.close()

def get_top_users(month, year, limit=10):
    conn = db_connector.get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        query = """
            SELECT 
                u.name, 
                u.email,
                SUM(b.booked_base_price - COALESCE((SELECT SUM(amount_deducted) FROM booking_discounts bd WHERE bd.booking_id = b.booking_id), 0)) as total_spent
            FROM booking b
            JOIN user u ON b.user_id = u.user_id
            WHERE b.status = 'confirmed'
            GROUP BY u.user_id, u.name, u.email
            ORDER BY total_spent DESC
            LIMIT %s
        """

        cursor.execute(query, (limit,))
        return cursor.fetchall()
    
    except Exception as e:
        print(f"Error fetching top users: {e}")
        return []
    
    finally:
        cursor.close()
    
def get_top_events(month, year, limit=5):
    conn = db_connector.get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
            SELECT 
                e.event_name,
                SUM(b.booked_base_price - COALESCE((SELECT SUM(amount_deducted) FROM booking_discounts bd WHERE bd.booking_id = b.booking_id), 0)) as total_revenue
            FROM booking b
            JOIN event e ON b.event_id = e.event_id
            WHERE b.status = 'confirmed' AND MONTH(e.start_date) = %s AND YEAR(e.start_date) = %s
            GROUP BY e.event_id, e.event_name
            ORDER BY total_revenue DESC
            LIMIT %s
        """
        cursor.execute(query, (month, year, limit))
        return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching top events: {e}")
        return []
    finally:
        cursor.close()