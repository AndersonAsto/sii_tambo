from flask import Blueprint, render_template

cashiers_bp = Blueprint('cajeros', __name__)

@cashiers_bp.route("/cajeros")
def cajeros():
    # Datos de prueba
    cajeros = [
        {"id": 1, "nombre": "Juan Pérez", "dni": "12345678", "email": "juan@tambo.com", "estado": True},
        {"id": 2, "nombre": "Ana López", "dni": "87654321", "email": "ana@tambo.com", "estado": False},
    ]
    return render_template("cashiers.html", cajeros=cajeros)
