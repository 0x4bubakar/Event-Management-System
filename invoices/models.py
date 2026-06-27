from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Spacer, Paragraph, Table, SimpleDocTemplate, TableStyle, XPreformatted
from reportlab.graphics.charts.barcharts import VerticalBarChart
from datetime import datetime as dt

# General structure:
# LETTERHEAD
# Bristol Community Events (left adj.) [spaces] Order #xyz (right adj.)
# BODY
# SUBHEADING: "Invoice"
# User's name
# Email address
# Spacer
# Event name
# Dates - X tickets
# Booked on (timestamp)
# HUGE SPACER
# TABLE
# TABLE HEADINGS: Event name | Qty | # of days booked | Total
# Underneath TABLE:
# Subtotal: (sum of all tickets)
# Early bird discount (?%): -£ X.YZ
# Student discount (10%): -£ X.YZ
# HORIZONTAL RULE
# Total due: £ X.YZ 

# Discounts likely to be handled as a dict -> discounts = {"isStudent": True, "earlyBird": (probably a choice of numbers for each one)}
def receipt(timestamp, booking_number, event_name, days_booked, discounts, original_price, final_price):
    filename = f"Your Bristol Community Events Receipt - {timestamp.strftime("%d %B %Y")}.pdf"
    doc = SimpleDocTemplate(filename, pagesize=A4, topMargin=20*mm, bottomMargin=20*mm, leftMargin=20*mm, rightMargin=20*mm)
    styles = getSampleStyleSheet()
    story = []
    logo = Paragraph('<b>Bristol Community Events</b>', styles['Title'])
    booking_num_text = f"Booking #{booking_number}"
    booking_num = Paragraph(booking_num_text)
    header = Table([logo, booking_num])
    header.setStyle(TableStyle)