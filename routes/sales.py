from flask import Blueprint, request, redirect, url_for, session, flash, render_template
from datetime import datetime
from models.products import Producto
from models.sale import Venta
from models.saleDetail import DetalleVenta
from models.category import Categoria
from models.subCategory import SubCategoria
from models.producto_tienda import ProductoTienda
from config.config import db

sales_bp = Blueprint('sales', __name__)

@sales_bp.route("/sales", methods=["GET", "POST"])
def sales():
    # 1️⃣ Validar sesión
    if "cajero_id" not in session:
        flash("Debes iniciar sesión primero", "warning")
        return redirect(url_for("cajeros.login"))

    id_usuario = session["cajero_id"]
    id_tienda = session["idTienda"]

    # 2️⃣ Registrar nueva venta
    if request.method == "POST":
        productos = request.form.getlist("producto_id[]")
        cantidades = request.form.getlist("cantidad[]")

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

        # Crear venta vinculada al cajero y tienda
        venta = Venta(
            idTienda=id_tienda,
            idUsuario=id_usuario,
            cantidadProductos=sum(i["cantidad"] for i in items),
            total=total,
            createdAt=datetime.utcnow()
        )

        db.session.add(venta)
        db.session.flush()  # para obtener idVenta antes del commit

        # Crear detalles de venta
        for item in items:
            detalle = DetalleVenta(
                idVenta=venta.idVenta,
                idProducto=item["producto"].idProducto,
                cantidad=item["cantidad"],
                subtotal=item["subtotal"]
            )
            db.session.add(detalle)

            # Restar stock solo de la tienda actual
            stock_tienda = ProductoTienda.query.filter_by(
                idProducto=item["producto"].idProducto,
                idTienda=id_tienda
            ).first()
            if stock_tienda:
                stock_tienda.stockActual -= item["cantidad"]

        db.session.commit()
        flash("✅ Venta registrada correctamente", "success")
        return redirect(url_for("sales.sales"))

    # 3️⃣ Mostrar datos filtrados por tienda
    categorias = Categoria.query.all()
    subcategorias = SubCategoria.query.all()

    # Productos solo de la tienda del cajero
    productos_tienda = (
        db.session.query(Producto)
        .join(ProductoTienda)
        .filter(ProductoTienda.idTienda == id_tienda)
        .all()
    )

    # Historial de ventas solo de esta tienda
    historial = (
        Venta.query.filter_by(idTienda=id_tienda)
        .order_by(Venta.createdAt.desc())
        .all()
    )

    return render_template(
        "sales_panel.html",
        categorias=categorias,
        subcategorias=subcategorias,
        productos=productos_tienda,
        historial=historial
    )
