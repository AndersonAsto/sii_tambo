from flask import Blueprint, render_template, request, url_for, flash, redirect, session
from models.cashiers import Cajeros
from models.store import Store
from config.config import db
from werkzeug.security import generate_password_hash, check_password_hash

cajeros_bp = Blueprint("cajeros", __name__)

@cajeros_bp.route("/cajeros")
def listado():
    cajeros = Cajeros.query.all()
    return render_template("cashiers.html", cajeros=cajeros)

@cajeros_bp.route("/nuevo", methods=["GET", "POST"])
def nuevo_cajero():
    if request.method == "POST":
        email = request.form["email"]
        contrasenia = request.form["contrasenia"]
        idTienda = request.form["idTienda"]

        nuevo = Cajeros(
            codUsuario="USR001",  # luego lo generamos dinámicamente
            idTienda=idTienda,
            email=email,
            contrasenia=generate_password_hash(contrasenia),
            estado=True
        )

        db.session.add(nuevo)
        db.session.commit()
        flash("Cajero agregado exitosamente", "success")
        return redirect(url_for("cajeros.listado"))

    # En caso GET, mostrar formulario
    return render_template("nuevo_cajero.html")

# Ruta de login
@cajeros_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        contrasenia = request.form["contrasenia"]

        # Buscar al cajero en la BD
        cajero = Cajeros.query.filter_by(email=email).first()

        if cajero and check_password_hash(cajero.contrasenia, contrasenia):
            session["cajero_id"] = cajero.idUsuario
            session["cajero_nombre"] = cajero.email
            return redirect(url_for("cajeros.dashboard"))
        else:
            flash("Correo o contraseña incorrectos", "danger")

    return render_template("cashiers_login.html")


# Panel exclusivo del cajero
@cajeros_bp.route("/dashboard")
def dashboard():
    if "cajero_id" not in session:
        flash("Debes iniciar sesión primero", "warning")
        return redirect(url_for("cajeros.login"))

    cajero = Cajeros.query.get(session["cajero_id"])
    return render_template("cashiers_index.html", cajero=cajero)


# Logout
@cajeros_bp.route("/logout")
def logout():
    session.clear()
    flash("Sesión cerrada correctamente", "success")
    return redirect(url_for("cajeros.login"))