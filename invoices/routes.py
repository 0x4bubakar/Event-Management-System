from flask import Blueprint, send_file, flash, redirect, url_for, session
from utils.decorators import is_logged_in
from .models import receipt
from booking.models import get_booking_details, get_cancellation_data

invoices_bp = Blueprint('invoices', __name__)

@invoices_bp.route('/download-receipt/<int:booking_id>', methods=['GET'])
@is_logged_in
def download_receipt(booking_id):
    user_id = session.get('user_id')
    booking_data = get_booking_details(user_id, booking_id)
    cancellation_data = get_cancellation_data(user_id, booking_id)
    if not booking_data:
        flash("Receipt not found or you do not have permission to view it.", "flash-error")
        return redirect(url_for('users.dashboard'))
    
    pdf_buffer = receipt(
        booked_on=booking_data['booked_on'],
        booking_id=booking_data['booking_id'],
        attendee_name=booking_data['attendee_name'],
        days_booked=booking_data['days_booked'],
        discounts=booking_data['discounts'],
        original_price=float(booking_data['booked_base_price']),
        final_price=float(booking_data['final_price']),
        status=booking_data['status'],
        event_name=booking_data['event_name'],
        cancel_data=cancellation_data
    )

    filename = f"BCE_Invoice_Order_{booking_id}.pdf"

    return send_file(pdf_buffer, mimetype='application/pdf', as_attachment=True, download_name=filename)