"""
Simulación de ventas optimizada para la base de datos `sistema_tambo`.
Genera registros en `siit_ventas` y `siit_detalle_ventas` desde 2023-01-01 hasta 2025-11-16.

DEPENDENCIAS:
  pip install mysql-connector-python pandas numpy faker tqdm

CARACTERÍSTICAS:
- Sin manejo de stock (eliminado para maximizar rendimiento).
- Inserciones por lotes tanto en ventas como en detalles.
- Commits agrupados por cada N tiendas (reduce I/O).
- Simulación realista de fechas y productos.
- Compatible con DRY_RUN y LIMIT_STORES para pruebas.

USO:
  python simulate_ventas_fast.py
"""

import random
from datetime import datetime, timedelta, time
import mysql.connector
import pandas as pd
import numpy as np
from faker import Faker
from tqdm import tqdm

# -------------------------
# CONFIGURACIÓN
# -------------------------
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'sistema_tambo',
    'raise_on_warnings': True
}

START_DATE = datetime(2023, 1, 1)
END_DATE = datetime(2025, 11, 16, 23, 59, 59)
MIN_SALES_PER_STORE = 50
MAX_SALES_PER_STORE = 150
SALES_BATCH_SIZE = 500  # ventas por lote
DETAILS_BATCH_SIZE = 2000  # detalles por lote
COMMIT_EVERY_N_STORES = 10
DRY_RUN = False
LIMIT_STORES = None

fake = Faker()
np.random.seed(42)
random.seed(42)

# Pesos base por categoría
CATEGORY_BASE_WEIGHTS = {
    'Licores': 0.04, 'RTDs': 0.06, 'Cigarros y vapes': 0.05,
    'Bebidas': 0.18, 'Comidas': 0.15, 'Despensa': 0.14,
    'Confiteria': 0.10, 'Antojos': 0.08, 'Helados': 0.06,
    'Cervezas': 0.09, 'Promociones': 0.12, 'Marcas Tambo': 0.10, 'Zonas': 0.05
}


def random_datetime_between(start_date, end_date):
    """Genera datetime aleatorio entre start_date y end_date con hora entre 08:00 y 22:00."""
    total_days = (end_date.date() - start_date.date()).days
    base_day = start_date.date() + timedelta(days=random.randint(0, total_days))
    hour = random.randint(8, 21)
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    return datetime.combine(base_day, time(hour, minute, second))


def normalize_weights(d):
    s = sum(d.values())
    return {k: v / s for k, v in d.items()} if s else {k: 1 / len(d) for k in d}


def to_native(val):
    if isinstance(val, (np.generic,)):
        return val.item()
    return val


def main():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)

    try:
        # Cargar tiendas
        cursor.execute("SELECT idTienda, codTienda FROM siit_tiendas ORDER BY idTienda")
        tiendas = cursor.fetchall()
        if LIMIT_STORES:
            tiendas = tiendas[:LIMIT_STORES]

        print(f"Tiendas a procesar: {len(tiendas)}")

        # Cargar usuarios
        cursor.execute("SELECT idUsuario, idTienda FROM siit_usuarios")
        user_by_store = {u['idTienda']: u['idUsuario'] for u in cursor.fetchall()}

        # Cargar productos
        query = '''
        SELECT p.idProducto, p.precioNuevo, c.categoria
        FROM siit_productos p
        JOIN siit_categorias c ON p.idCategoria = c.idCategoria
        WHERE p.estado = 1
        '''
        cursor.execute(query)
        productos = cursor.fetchall()
        if not productos:
            raise RuntimeError("No hay productos activos en siit_productos")

        prod_df = pd.DataFrame(productos)
        cat_weights = CATEGORY_BASE_WEIGHTS.copy()
        for cat in prod_df['categoria'].unique():
            if cat not in cat_weights:
                cat_weights[cat] = 0.08
        cat_weights = normalize_weights(cat_weights)

        alpha = 0.6
        prod_df['cat_weight'] = prod_df['categoria'].map(cat_weights)
        prod_df['price_factor'] = 1.0 / (prod_df['precioNuevo'].astype(float) ** alpha + 1e-6)
        prod_df['raw_weight'] = prod_df['cat_weight'] * prod_df['price_factor']
        prod_df['weight'] = prod_df['raw_weight'] / prod_df['raw_weight'].sum()

        prod_ids = prod_df['idProducto'].tolist()
        prod_weights = prod_df['weight'].tolist()

        insert_venta_sql = "INSERT INTO siit_ventas (idTienda, idUsuario, cantidadProductos, total, createdAt) VALUES (%s, %s, %s, %s, %s)"
        insert_detalle_sql = "INSERT INTO siit_detalle_ventas (idVenta, idProducto, cantidad, subtotal, createdAt) VALUES (%s, %s, %s, %s, %s)"

        ventas_batch = []
        detalles_batch = []
        total_ventas = 0
        total_detalles = 0

        for i, tienda in enumerate(tqdm(tiendas, desc="Simulando tiendas")):
            id_tienda = tienda['idTienda']
            id_usuario = user_by_store.get(id_tienda)
            num_sales = random.randint(MIN_SALES_PER_STORE, MAX_SALES_PER_STORE)

            for _ in range(num_sales):
                venta_dt = random_datetime_between(START_DATE, END_DATE)
                num_items = random.randint(1, 6)
                chosen_products = np.random.choice(prod_ids, size=num_items, replace=False, p=prod_weights)

                detalles = []
                total_venta = 0
                cantidad_total = 0

                for pid in chosen_products:
                    precio = float(prod_df.loc[prod_df['idProducto'] == pid, 'precioNuevo'].iloc[0])
                    cantidad = max(1, np.random.poisson(1.8))
                    subtotal = round(precio * cantidad, 2)
                    detalles.append((pid, cantidad, subtotal))
                    total_venta += subtotal
                    cantidad_total += cantidad

                # ✅ Insertar una venta, obtener su id exacto
                cursor.execute(insert_venta_sql, (id_tienda, id_usuario, cantidad_total, round(total_venta, 2), venta_dt))
                venta_id = cursor.lastrowid
                total_ventas += 1

                # ✅ Acumular detalles con idVenta real
                for pid, q, sub in detalles:
                    detalles_batch.append((venta_id, pid, q, sub, venta_dt))
                    total_detalles += 1

                if len(detalles_batch) >= DETAILS_BATCH_SIZE:
                    cursor.executemany(insert_detalle_sql, [tuple(to_native(v) for v in row) for row in detalles_batch])
                    detalles_batch.clear()

            # Commit cada N tiendas
            if (i + 1) % COMMIT_EVERY_N_STORES == 0 and not DRY_RUN:
                conn.commit()

        # Insertar los detalles restantes
        if detalles_batch:
            cursor.executemany(insert_detalle_sql, [tuple(to_native(v) for v in row) for row in detalles_batch])
            detalles_batch.clear()


        if not DRY_RUN:
            conn.commit()

        print(f"\n✅ Ventas generadas: {total_ventas:,}")
        print(f"✅ Detalles generados: {total_detalles:,}")

    except Exception as e:
        conn.rollback()
        print("❌ Error durante la simulación:", e)
        raise
    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    main()
