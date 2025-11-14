from flask import Blueprint, render_template, request, url_for, flash, redirect, session
from models.cashiers import Cajeros
from models.category import Categoria
from models.subCategory import SubCategoria
from models.producto_tienda import ProductoTienda
from models.products import Producto
from models.sale import Venta
from config.config import db
from werkzeug.security import generate_password_hash, check_password_hash

cajeros_bp = Blueprint("cajeros", __name__)

# --------------------------
# LISTADO DE CAJEROS
# --------------------------
@cajeros_bp.route("/cajeros")
def listado():
    cajeros = Cajeros.query.all()
    return render_template("cashiers.html", cajeros=cajeros)


# --------------------------
# NUEVO CAJERO
# --------------------------
@cajeros_bp.route("/nuevo", methods=["GET", "POST"])
def nuevo_cajero():
    if request.method == "POST":
        email = request.form["email"]
        contrasenia = request.form["contrasenia"]
        idTienda = request.form["idTienda"]

        nuevo = Cajeros(
            codUsuario="USR001",  # luego se genera dinámico
            idTienda=idTienda,
            email=email,
            contrasenia=generate_password_hash(contrasenia),
            estado=True
        )

        db.session.add(nuevo)
        db.session.commit()

        flash("Cajero agregado exitosamente", "success")
        return redirect(url_for("cajeros.listado"))

    return render_template("nuevo_cajero.html")


# --------------------------
# PANEL PRINCIPAL DEL CAJERO (VENTAS)
# --------------------------
@cajeros_bp.route("/sales")
def sales_panel():
    if "cajero_id" not in session:
        flash("Debes iniciar sesión primero", "warning")
        return redirect(url_for("cajeros.login"))

    # Tomar datos de sesión
    id_tienda = session["idTienda"]

    # ------------ CARGA REAL DE DATOS (IGUAL QUE sales.sales) ----------------
    categorias = Categoria.query.all()
    subcategorias = SubCategoria.query.all()

    productos_tienda = (
        db.session.query(Producto)
        .join(ProductoTienda)
        .filter(ProductoTienda.idTienda == id_tienda)
        .all()
    )

    historial = (
        Venta.query.filter_by(idTienda=id_tienda)
        .order_by(Venta.createdAt.desc())
        .all()
    )

    # Renderizar con datos cargados
    return render_template(
        "sales_panel.html",
        categorias=categorias,
        subcategorias=subcategorias,
        productos=productos_tienda,
        historial=historial
    )


# --------------------------
# LOGIN
# --------------------------
@cajeros_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        contrasenia = request.form["contrasenia"]

        cajero = Cajeros.query.filter_by(email=email).first()

        if cajero and check_password_hash(cajero.contrasenia, contrasenia):

            # Guardar sesión
            session["cajero_id"] = cajero.idUsuario
            session["cajero_nombre"] = cajero.email
            session["idTienda"] = cajero.idTienda

            # Redirigir al panel de ventas del cajero
            return redirect(url_for("cajeros.sales_panel"))

        else:
            flash("Correo o contraseña incorrectos", "danger")

    # Mostrar formulario de login en GET
    return render_template("cashiers_login.html")


# --------------------------
# DASHBOARD → redirige a ventas
# --------------------------
@cajeros_bp.route("/dashboard")
def dashboard():
    if "cajero_id" not in session:
        flash("Debes iniciar sesión primero", "warning")
        return redirect(url_for("cajeros.login"))

    return redirect(url_for("cajeros.sales_panel"))


# --------------------------
# LOGOUT
# --------------------------
@cajeros_bp.route("/logout")
def logout():
    session.clear()
    flash("Sesión cerrada correctamente", "success")
    return redirect(url_for("cajeros.login"))
