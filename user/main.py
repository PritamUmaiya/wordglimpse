from flask import Blueprint, render_template

# Create a Blueprint
main_bp = Blueprint('route', __name__)


''' ---- Index page routes ---- '''
@main_bp.route("/")
@main_bp.route("/home")
@main_bp.route("/following")
@main_bp.route("/saved")
def index():
    return render_template("layout.html")