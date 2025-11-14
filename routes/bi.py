from flask import Blueprint, render_template

bi_bp = Blueprint("bi", __name__)

@bi_bp.route("/")
def index():
    return render_template("bi_dashboard.html")