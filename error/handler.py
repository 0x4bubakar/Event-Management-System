from flask import Blueprint, render_template
error_bp = Blueprint('error', __name__)

@error_bp.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404