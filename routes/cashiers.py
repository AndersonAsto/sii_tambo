from flask import Blueprint, render_template, request, url_for, flash, redirect
from models.cashiers import Cajeros
from models.store import Store
from config.config import db
from werkzeug.security import generate_password_hash

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