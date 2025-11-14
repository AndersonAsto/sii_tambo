from flask import Blueprint, render_template, session, redirect, url_for, flash, request
#from models.producto_tienda import ProductoTienda



stock_bp = Blueprint('stock', __name__)

#@stock_bp.route('/stock', methods=["GET", "POST"])
#def stock():
#    if "idTienda" not in session:
#        flash("Debes iniciar sesión como cajero", "warning")
#        return redirect(url_for("cajeros.login"))
    
#    tienda_id = session["idTienda"]

#    Productos = ProductoTienda.query.filter_by(idTienda=tienda_id).all()

#    return render_template(
#        'stock_panel.html',
#        stock= Productos
        


@stock_bp.route('/stock', methods=["GET"])
def stock_dashboard():

    if "idTienda" not in session:
        flash("Debes iniciar sesión como cajero", "warning")
        return redirect(url_for("cajeros.login"))

    # ENLACE PUBLICADO EN POWER BI
    power_bi_url = "AQUI VA EL ENLACE"

    return render_template(
        'dashboard_stock.html',
        power_bi_url=power_bi_url
    )
