import os
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

from config.config import db
from models.sale import Venta
from models.store import Store


def generar_reporte_pdf(departamento=None, provincia=None, distrito=None):
    # ======================
    #   FILTRAR VENTAS
    # ======================
    venta_query = Venta.query.join(Store)

    if departamento:
        venta_query = venta_query.filter(Store.departamento == departamento)

    if provincia:
        venta_query = venta_query.filter(Store.provincia == provincia)

    if distrito:
        venta_query = venta_query.filter(Store.distrito == distrito)

    ventas = venta_query.order_by(Venta.createdAt.desc()).all()

    # ======================
    #   RESUMEN SIMPLE
    # ======================
    total_ventas = len(ventas)
    monto_total = sum(v.total for v in ventas) if total_ventas > 0 else 0

    # ======================
    #   CREAR PDF
    # ======================
    folder_path = "static/reports"
    os.makedirs(folder_path, exist_ok=True)

    filename = f"reporte_ventas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    file_path = os.path.join(folder_path, filename)

    pdf = SimpleDocTemplate(file_path, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    # ======================
    # TITULO
    # ======================
    titulo = "<b>Reporte de Ventas</b>"
    elements.append(Paragraph(titulo, styles["Title"]))
    elements.append(Spacer(1, 10))

    # ======================
    # RESUMEN MINIMO
    # ======================
    resumen = f"""
        <b>Total de Ventas:</b> {total_ventas}<br/>
        <b>Monto Total:</b> S/ {round(monto_total, 2)}
    """

    elements.append(Paragraph(resumen, styles["Normal"]))
    elements.append(Spacer(1, 15))

    # ======================
    # TABLA DE VENTAS
    # ======================
    if total_ventas == 0:
        elements.append(Paragraph("<b>No se encontraron ventas.</b>", styles["Normal"]))
    else:
        data = [["ID Venta", "Tienda", "Total", "Fecha"]]

        for v in ventas:
            data.append([
                v.idVenta,
                v.tienda.tienda if v.tienda else "N/A",
                f"S/ {v.total}",
                v.createdAt.strftime("%d/%m/%Y %H:%M")
            ])

        tabla = Table(data, repeatRows=1)
        tabla.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#003366")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ]))

        elements.append(tabla)

    # ======================
    # GENERAR PDF
    # ======================
    pdf.build(elements)
    return filename
