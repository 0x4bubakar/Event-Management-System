from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Spacer, Paragraph, Table, SimpleDocTemplate, TableStyle
from reportlab.graphics.charts.barcharts import VerticalBarChart
from io import BytesIO
from datetime import datetime as dt

def receipt(booked_on, booking_id, attendee_name, event_name, days_booked, discounts, original_price, final_price, status, cancel_data):
    # using the io library, create an in-memory bytes stream for the pdf
    # this creates the pdfs in memory and thus means we do not need to store them as they are generated dynamically
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=20*mm, bottomMargin=20*mm, leftMargin=20*mm, rightMargin=20*mm)
    styles = getSampleStyleSheet()
    story = []
    now = dt.now()

    title_style = styles['Title']
    title_style.alignment = 0
    normal = styles['Normal']
    heading = styles['Heading2']
    right_align_normal = ParagraphStyle('RightAlign', parent=normal, alignment=2)

    # letterhead
    logo = Paragraph('<b>Bristol Community Events</b>', title_style)
    booking_num = Paragraph(f"Order #{booking_id}", right_align_normal)

    header_table = Table([[logo, booking_num]], colWidths=[110*mm, 60*mm])
    header_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (0,0), 'LEFT'), # left align BCE logo inside cell
        ('ALIGN', (1,0), (1,0), 'RIGHT'), # right align order number
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE') # vertically centre all cells
    ]))

    story.append(header_table)
    story.append(Spacer(1,15*mm))

    # body of receipt
    if status == "cancelled":
        story.append(Paragraph('<font color="red"><b>Cancellation Receipt</b></font>', heading))
    else:
        story.append(Paragraph('<b>Invoice</b>', heading))
    story.append(Paragraph(f"<b>Attendee: </b>{attendee_name}", normal))
    story.append(Paragraph(f"<b>Event:</b>{event_name}", normal))
    story.append(Paragraph(f"<b>Days booked: </b>{days_booked} days", normal))
    story.append(Paragraph(f"<b>Booked on: </b>{booked_on.strftime('%d/%m/%Y - %H:%M')}", normal))
    story.append(Paragraph(f"<b>Receipt generated on: </b>{now.strftime('%d/%m/%Y - %H:%M')}", normal))

    story.append(Spacer(1, 20*mm))

    table_data = [
        ['Event Name', 'Days Booked', 'Subtotal'],
        [event_name, str(days_booked), f"£{original_price:.2f}"]
    ]

    order_table = Table(table_data, colWidths=[70*mm, 25*mm, 25*mm])
    order_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightblue),
        ('TEXTCOLOR', (0,0), (-1, -1), colors.black),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 1, colors.black), # black grid with a thickness of 1 pixel
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
    ]))

    story.append(order_table)
    story.append(Spacer(1, 10*mm))

    for discount in discounts:
        discount_name = discount['name']
        percent = discount['percent']
        amount_deducted = discount['amount']

        story.append(Paragraph(f"{discount_name} ({percent}% off): -£{amount_deducted:.2f}", normal))

    story.append(Spacer(1,5*mm))
    story.append(Paragraph(f"<b>Amount paid: </b>£{final_price:.2f}", normal))

    if status == "cancelled" and cancel_data is not None:

        cancel_on = cancel_data['cancelled_on']
        cancel_fee = float(cancel_data['cancellation_fee'])

        refund_amount = final_price - cancel_fee

        if cancel_fee == 0:
            cancel_tier = "(No cancellation fee applied - booking was cancelled at least 40 days before the event.)"
        elif cancel_fee == final_price:
            cancel_tier = "(100% cancellation fee - booking was cancelled under 25 days before the event)"
        else:
            cancel_tier = "(40% cancellation fee - booking was cancelled 25-39 days before the event)"

        formatted_cancel_date = cancel_on.strftime('%d/%m/%Y - %H:%M')

        story.append(Spacer(1, 5*mm))
        story.append(Paragraph(f"<b>Cancelled on: </b> {formatted_cancel_date}", normal))
        story.append(Paragraph(f"<b>Cancellation fee: </b>-£{cancel_fee:.2f} {cancel_tier}", normal))
        story.append(Paragraph(f"<b>Total refunded: </b>£{refund_amount:.2f}", normal))
        
    doc.build(story)
    buffer.seek(0)

    return buffer
    
if __name__ == "__main__": # if file is ran directly (i.e. python3 /invoices/models.py), run the test script below
    # create dummy discounts
    test_discounts = [
        {'name': 'Student Discount', 'percent': 10, 'amount': 15.00},
        {'name': 'Early Bird (35-50 Days)', 'percent': 15, 'amount': 22.50}
    ]

    # call the function with test data
    receipt(
        booked_on=dt.now(),
        booking_number=1042,
        attendee_name="John Smith",
        event_name="Lorem Ipsum Con 2026",
        days_booked=7,
        discounts=test_discounts,
        original_price=150.00,
        final_price=112.50
    )
    print("Test PDF generated successfully! Check your project folder.")