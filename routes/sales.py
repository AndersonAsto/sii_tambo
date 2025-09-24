from flask import Blueprint, render_template, request

sales_bp = Blueprint('sales', __name__)

@sales_bp.route('/sales')
def sales():
    return render_template(
        'sales_panel.html'
    )