from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.store import Store
from models.sale import Venta
from config.config import db
from data.etl import run_etl

total_sales_bp = Blueprint("totalsales", __name__)

@total_sales_bp.route("/")
def index():
    page = request.args.get("page", 1, type=int)
    per_page = 20

    # 🔹 Recibir filtros del formulario
    departamento = request.args.get("departamento")
    provincia = request.args.get("provincia")
    distrito = request.args.get("distrito")

    # ================================
    #   FILTRO DE TIENDAS
    # ================================
    store_query = Store.query

    if departamento:
        store_query = store_query.filter_by(departamento=departamento)
    if provincia:
        store_query = store_query.filter_by(provincia=provincia)
    if distrito:
        store_query = store_query.filter_by(distrito=distrito)

    # Lista final de tiendas filtradas
    filtered_stores = store_query.all()
    store_ids = [s.idTienda for s in filtered_stores]

    # ================================
    #   CONSULTA DE VENTAS
    # ================================
    venta_query = Venta.query

    if store_ids:
        venta_query = venta_query.filter(Venta.idTienda.in_(store_ids))

    # Orden descendente por fecha (más reciente primero)
    venta_query = venta_query.order_by(Venta.createdAt.desc())

    # Paginación de ventas
    ventas = venta_query.paginate(page=page, per_page=per_page, error_out=False)

    # ================================
    #   FILTROS ÚNICOS
    # ================================
    departamentos = [d[0] for d in db.session.query(Store.departamento).distinct().all()]
    provincias = [p[0] for p in db.session.query(Store.provincia).distinct().all()]
    distritos = [dist[0] for dist in db.session.query(Store.distrito).distinct().all()]

    # Diccionario Dep → Prov → Dist
    dep_prov_dist = {}
    all_stores = Store.query.all()
    for s in all_stores:
        dep = s.departamento
        prov = s.provincia
        dist = s.distrito
        dep_prov_dist.setdefault(dep, {}).setdefault(prov, []).append(dist)

    return render_template(
        "total_sales.html",
        ventas=ventas,                    # 👈 LISTA DE VENTAS PAGINADAS
        departamentos=departamentos,
        provincias=provincias,
        distritos=distritos,
        dep_prov_dist=dep_prov_dist,
        departamento_sel=departamento,
        provincia_sel=provincia,
        distrito_sel=distrito
    )

@total_sales_bp.route("/detalle/<int:idVenta>")
def detalle(idVenta):
    venta = Venta.query.get_or_404(idVenta)
    detalles = venta.detalles  # relación ya definida

    return render_template("components/detalle_modal.html", venta=venta, detalles=detalles)

@total_sales_bp.route("/enviar-almacen", methods=["POST"])
def enviar_alamacen():
    try:
        run_etl()  # Ejecuta el ETL completo

        flash("✔ Datos enviados exitosamente al almacén de datos.", "success")
        return redirect(url_for("totalsales.index"))

    except Exception as e:
        print(f"ERROR interno en ETL: {e}")  # NO mostrar al usuario
        flash("⚠ No se pudo enviar los datos al almacén. Inténtalo más tarde.", "danger")
        return redirect(url_for("totalsales.index"))
    
@total_sales_bp.route("/reporte-pdf")
def reporte_pdf():
    from data.informe import generar_reporte_pdf

    departamento = request.args.get("departamento")
    provincia = request.args.get("provincia")
    distrito = request.args.get("distrito")

    pdf_path = generar_reporte_pdf(
        departamento=departamento,
        provincia=provincia,
        distrito=distrito
    )

    return redirect(url_for("static", filename=f"reports/{pdf_path}"))
