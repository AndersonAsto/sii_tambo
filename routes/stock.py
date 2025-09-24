from flask import Blueprint, render_template, request

stock_bp = Blueprint('stock', __name__)

@stock_bp.route('/stock')
def stock():
    return render_template(
        'stock_panel.html'
    )