from flask import Blueprint, redirect, render_template, url_for, request, flash, session
from utils.decorators import is_logged_in, is_admin
from .models import get_revenue_reports

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/admin/reports', methods=['GET'])
@is_logged_in
@is_admin
def admin_reports():
    revenue_data = get_revenue_reports()
    grand_total = sum(float(row['total_revenue']) for row in revenue_data)
    return render_template('admin-reports.html', reports=revenue_data, grand_total=grand_total)