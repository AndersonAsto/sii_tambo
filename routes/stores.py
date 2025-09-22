from flask import Blueprint, render_template, request, redirect, url_for
from config.config import db
from models.store import Store

stores_bp = Blueprint("stores", __name__)

@stores_bp.route("/")
def index():
    page = request.args.get("page", 1, type=int)
    per_page = 20

    # 🔹 Recibir filtros del formulario
    departamento = request.args.get("departamento")
    provincia = request.args.get("provincia")
    distrito = request.args.get("distrito")

    # 🔹 Consulta base
    query = Store.query

    # 🔹 Aplicar filtros si se seleccionaron
    if departamento:
        query = query.filter_by(departamento=departamento)
    if provincia:
        query = query.filter_by(provincia=provincia)
    if distrito:
        query = query.filter_by(distrito=distrito)

    # 🔹 Paginación
    stores = query.paginate(page=page, per_page=per_page, error_out=False)

    # 🔹 Preparar lista única de departamentos, provincias y distritos
    departamentos = [d[0] for d in db.session.query(Store.departamento).distinct().all()]
    provincias = [p[0] for p in db.session.query(Store.provincia).distinct().all()]
    distritos = [dist[0] for dist in db.session.query(Store.distrito).distinct().all()]

    # 🔹 Preparar diccionario para filtro encadenado
    dep_prov_dist = {}
    all_stores = Store.query.all()
    for s in all_stores:
        dep = s.departamento
        prov = s.provincia
        dist = s.distrito
        if dep not in dep_prov_dist:
            dep_prov_dist[dep] = {}
        if prov not in dep_prov_dist[dep]:
            dep_prov_dist[dep][prov] = []
        if dist not in dep_prov_dist[dep][prov]:
            dep_prov_dist[dep][prov].append(dist)

    return render_template(
        "stores.html",
        stores=stores,
        departamentos=departamentos,
        provincias=provincias,
        distritos=distritos,
        dep_prov_dist=dep_prov_dist
    )


@stores_bp.route("/create", methods=["GET", "POST"])
def create():
    if request.method == "POST":
        codigo = request.form["codigo"]
        nombre = request.form["nombre"]
        direccion = request.form["direccion"]

        store = Store(codigo=codigo, nombre=nombre, direccion=direccion)
        db.session.add(store)
        db.session.commit()

        return redirect(url_for("stores.index"))
    return render_template("create_store.html")

@stores_bp.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    store = Store.query.get_or_404(id)

    if request.method == "POST":
        store.codigo = request.form["codigo"]
        store.nombre = request.form["nombre"]
        store.direccion = request.form["direccion"]

        db.session.commit()
        return redirect(url_for("stores.index"))

    return render_template("edit_store.html", store=store)


@stores_bp.route("/delete/<int:id>", methods=["POST", "GET"])
def delete(id):
    store = Store.query.get_or_404(id)
    db.session.delete(store)
    db.session.commit()
    return redirect(url_for("stores.index"))
