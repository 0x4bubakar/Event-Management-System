import db_connector
from reportlab import *

def get_revenue_reports():
    conn = db_connector.get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        query = """
            SELECT e.event_id, e.event_name, e.start_date,
            COUNT(b.booking_id) AS total_bookings,
            COALESCE(SUM(b.final_price), 0) AS total_revenue
            FROM event e
            LEFT JOIN booking b ON event.event_id = b.event_id AND b.status = 'confirmed'
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