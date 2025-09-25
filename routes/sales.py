from flask import Blueprint, request, redirect, url_for, session, flash, render_template
from models.products import Producto
from models.sale import Venta
from models.saleDetail import DetalleVenta
from models.category import Categoria
from models.subCategory import SubCategoria
from config.config import db

sales_bp = Blueprint('sales', __name__)

@sales_bp.route("/sales", methods=["GET", "POST"])
def sales():
    if "cajero_id" not in session:
        flash("Debes iniciar sesión primero", "warning")
        return redirect(url_for("cajeros.login"))

    if request.method == "POST":
        productos = request.form.getlist("producto_id[]")
        cantidades = request.form.getlist("cantidad[]")

        id_usuario = session["cajero_id"]
        id_tienda = session["idTienda"]

        total = 0
        items = []

        for prod_id, cant in zip(productos, cantidades):
            producto = Producto.query.get(int(prod_id))
            if not producto or int(cant) <= 0:
                continue

            subtotal = producto.precioNuevo * int(cant)
            total += subtotal
            items.append({"producto": producto, "cantidad": int(cant), "subtotal": subtotal})

        if not items:
            flash("Debes seleccionar al menos un producto", "danger")
            return redirect(url_for("sales.sales"))

        venta = Venta(
            idTienda=id_tienda,
            idUsuario=id_usuario,
            cantidadProductos=sum([i["cantidad"] for i in items]),
            total=total
        )
        db.session.add(venta)
        db.session.flush()

        for item in items:
            detalle = DetalleVenta(
                idVenta=venta.idVenta,
                idProducto=item["producto"].idProducto,
                cantidad=item["cantidad"],
                subtotal=item["subtotal"]
            )
            db.session.add(detalle)

        db.session.commit()
        flash("✅ Venta registrada correctamente", "success")
        return redirect(url_for("sales.sales"))

    categorias = Categoria.query.all()
    subcategorias = SubCategoria.query.all()
    productos = Producto.query.all()
    return render_template("sales_panel.html", categorias=categorias, subcategorias=subcategorias, productos=productos)
