import random
import csv
from datetime import datetime, timedelta

from config.config import db, Config
from models.producto_tienda import ProductoTienda
from models.products import Producto
from models.store import Store

from flask import Flask

# Crear app Flask para usar SQLAlchemy
app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

# Diccionario con reglas de stock (como ya lo tienes)
REGLAS_STOCK = {
    "1": {"1": (50, 10), "2": (20, 10), "3": (50, 10), "4": (50, 10)},
    "2": {"5": (150, 20), "6": (40, 10), "7": (150, 30), "8": (100, 20), "9": (50, 10)},
    "3": {"10": (200, 30)},
    "4": {"11": (100, 10), "12": (20, 5)},
    "5": {"13": (30, 5), "14": (30, 5), "15": (30, 5), "16": (30, 5), "17": (30, 5)},
    "6": {"18": (100, 20), "19": (100, 20), "20": (100, 20), "21": (100, 20)},
    "7": {"22": (50, 10), "23": (40, 8), "24": (30, 5), "25": (50, 10),
          "26": (40, 8), "27": (100, 15), "28": (30, 5)},
    "8": {"29": (100, 20), "30": (100, 20)},
    "9": {"31": (60, 15), "32": (50, 12), "33": (40, 12), "34": (60, 15),
          "35": (45, 12), "36": (25, 12), "37": (60, 15), "38": (45, 12)},
    "10": {"39": (60, 15), "40": (45, 12), "41": (25, 8), "42": (45, 12), "43": (30, 5)},
    "11": {"44": (30, 8), "45": (45, 12), "46": (25, 8), "47": (30, 8),
           "48": (15, 4), "49": (25, 8)},
    "12": {"50": (100, 15)},
    "13": {"51": (25, 8), "52": (25, 8), "53": (25, 8), "54": (25, 8)},
    "default": (20, 5)
}


def generar_fecha_random():
    """Genera un datetime aleatorio entre 2024-01-30 08:00 y 2024-01-30 22:00"""
    inicio = datetime(2024, 1, 30, 8, 0, 0)
    fin = datetime(2024, 1, 30, 22, 0, 0)
    delta = fin - inicio
    segundos_random = random.randint(0, int(delta.total_seconds()))
    return inicio + timedelta(seconds=segundos_random)


def obtener_regla(producto):
    """Devuelve (stockActual, stockMinimo) según la categoría y subcategoría"""
    categoria = str(producto.idCategoria)
    subcategoria = str(producto.idSubCategoria)

    if categoria in REGLAS_STOCK:
        reglas_sub = REGLAS_STOCK[categoria]
        if subcategoria in reglas_sub:
            return reglas_sub[subcategoria]
        return REGLAS_STOCK["default"]

    return REGLAS_STOCK["default"]


def simular_datos_csv(nombre_archivo="productos_tiendas.csv"):
    with app.app_context():
        productos = Producto.query.all()
        tiendas = Store.query.all()

        total_registros = len(productos) * len(tiendas)

        with open(nombre_archivo, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            # Cabecera
            writer.writerow([
                "idProducto", "idTienda", "stockActual", "stockMinimo", "createdAt", "updatedAt"
            ])

            for producto in productos:
                regla_stock = obtener_regla(producto)
                for tienda in tiendas:
                    stock_actual = random.randint(regla_stock[0] - 5, regla_stock[0] + 5)
                    stock_minimo = regla_stock[1]
                    fecha = generar_fecha_random().strftime("%Y-%m-%d %H:%M:%S")

                    writer.writerow([
                        producto.idProducto,
                        tienda.idTienda,
                        stock_actual,
                        stock_minimo,
                        fecha,
                        fecha
                    ])

        print(f"✅ Archivo CSV generado: {nombre_archivo}")
        print(f"📊 Total registros simulados: {total_registros}")


if __name__ == "__main__":
    simular_datos_csv()
