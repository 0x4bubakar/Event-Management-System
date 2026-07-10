from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Spacer, Paragraph, Table, SimpleDocTemplate, TableStyle
from io import BytesIO
from datetime import datetime as dt
import calendar

def generate_admin_report(year, target_month, monthly_data, top_users, top_events):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=20*mm, bottomMargin=20*mm, leftMargin=20*mm, rightMargin=20*mm)
    styles = getSampleStyleSheet()
    story = []
    
    title_style = styles['Title']
    heading = styles['Heading2']
    normal = styles['Normal']

    story.append(Paragraph(f"<b>BCE Admin Report - {year}</b>", title_style))
    story.append(Paragraph(f"Generated on: {dt.now().strftime('%d/%m/%Y - %H:%M')}", normal))
    story.append(Spacer(1, 10*mm))

    # monthly revenue table
    story.append(Paragraph("<b>Annual Revenue Breakdown</b>", heading))
    story.append(Spacer(1, 5*mm))

    table_data = [['Month', 'Ticket Revenue', 'Cancellation Fees', 'Hosting Fees', 'Total Revenue']]
    total_tickets, cancel_fees, hosting_fees, grand_total = 0, 0, 0, 0
    
    for m in range(1, 13):
        month_name = calendar.month_abbr[m]
        ticket_rev = monthly_data[m]['ticket_revenue']
        can_fees = monthly_data[m]['cancellation_fees']
        h_fees = monthly_data[m]['hosting_fees']
        grand = monthly_data[m]['total']
        
        total_tickets += ticket_rev
        cancel_fees += can_fees
        hosting_fees += h_fees
        grand_total += grand
        
        table_data.append([month_name, f"£{ticket_rev:.2f}", f"£{can_fees:.2f}", f"£{h_fees:.2f}", f"£{grand:.2f}"])

    # totals row
    table_data.append(['TOTALS', f"£{total_tickets:.2f}", f"£{cancel_fees:.2f}", f"£{hosting_fees:.2f}", f"£{grand_total:.2f}"])

    revenue_table = Table(table_data, colWidths=[30*mm, 35*mm, 35*mm, 35*mm, 35*mm])
    revenue_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#3232aa')),
        ('TEXTCOLOR', (0,0), (-1, 0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('BACKGROUND', (0,-1), (-1,-1), colors.lightgrey),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
    ]))
    story.append(revenue_table)
    story.append(Spacer(1, 15*mm))

    # top grossing events table
    target_month_name = calendar.month_name[int(target_month)]
    story.append(Paragraph(f"<b>Top Grossing Events ({target_month_name} {year})</b>", heading))
    story.append(Spacer(1, 5*mm))

    if top_events:
        event_data = [['Event Name', 'Total Revenue']]
        for e in top_events:
            event_data.append([e['event_name'], f"£{e['total_revenue']:.2f}"])
        
        event_table = Table(event_data, colWidths=[120*mm, 50*mm])
        event_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#3232aa')),
            ('TEXTCOLOR', (0,0), (-1, 0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ]))
        story.append(event_table)
    else:
        story.append(Paragraph(f"No completed events found for {target_month_name} {year}.", normal))
    
    story.append(Spacer(1, 15*mm))

    # --- 3. Top Paying Users (All Time / Year) ---
    story.append(Paragraph("<b>Top Paying Users (All Time)</b>", heading))
    story.append(Spacer(1, 5*mm))

    if top_users:
        user_data = [['Name', 'Email', 'Total Spent']]
        for u in top_users:
            user_data.append([u['name'], u['email'], f"£{u['total_spent']:.2f}"])
            
        user_table = Table(user_data, colWidths=[50*mm, 70*mm, 50*mm])
        user_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#3232aa')),
            ('TEXTCOLOR', (0,0), (-1, 0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ]))
        story.append(user_table)

    doc.build(story)
    buffer.seek(0)
    return buffer