from flask import Blueprint, redirect, render_template, url_for, request, flash, session, send_file
from utils.decorators import is_logged_in, is_admin
from .models import get_monthly_revenue_for_year, get_top_users, get_top_events
from .generator import generate_admin_report
from datetime import datetime

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/admin/reports', methods=['GET', 'POST'])
@is_logged_in
@is_admin
def admin_reports():
    now = datetime.now()

    if request.method == 'POST':
        target_month = int(request.form.get('target_month'))
        target_year = int(request.form.get('target_year'))

        monthly_data = get_monthly_revenue_for_year(target_year)
        top_users = get_top_users(target_month, target_year, limit=5)
        top_events = get_top_events(target_month, target_year, limit=5)

        pdf_buffer = generate_admin_report(target_year, target_month, monthly_data, top_users, top_events)
        file_name = f"BCE_Admin_Report_{target_month}_{target_year}.pdf"
        return send_file(pdf_buffer, mimetype='application/pdf', as_attachment=True, download_name=file_name)
    
    return render_template('admin-reports.html', current_year=now.year, current_month=now.month)