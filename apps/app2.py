import os
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from config.config import Config
from models.products import Producto  # tu modelo de productos

# Crear motor y sesión
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=engine)
session = Session()

# Carpeta donde están los CSVs
output_folder = "output"

# Función para generar codProducto incremental por categoría/subcategoría
def generar_cod_producto(idCategoria, idSubCategoria):
    ultimo = (
        session.query(Producto)
        .filter_by(idCategoria=idCategoria, idSubCategoria=idSubCategoria)
        .order_by(Producto.idProducto.desc())
        .first()
    )
    if ultimo and ultimo.codProducto:
        try:
            # Extrae el número secuencial final
            sec = int(ultimo.codProducto.split("-")[-1])
        except Exception:
            sec = 0
    else:
        sec = 0
    nuevo_sec = str(sec + 1).zfill(4)
    return f"CAT{idCategoria}-SUB{idSubCategoria}-{nuevo_sec}"


# Recorremos todos los archivos CSV
for file in os.listdir(output_folder):
    if file.endswith(".csv"):
        try:
            # Obtener idCategoria y idSubCategoria desde el nombre del archivo
            file_name = file.replace(".csv", "")
            idCategoria, idSubCategoria = map(int, file_name.split("-"))

            # Leer CSV
            df = pd.read_csv(os.path.join(output_folder, file))

            # Renombrar columnas según la tabla
            df = df.rename(columns={
                "Producto": "producto",
                "Precio Antiguo": "precioAntiguo",
                "Precio Nuevo": "precioNuevo",
                "Descuento %": "descuento"
            })

            # Limpiar espacios y valores nulos
            df.columns = [col.strip() for col in df.columns]
            df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
            df = df.dropna(subset=["producto"])
            df = df[df["producto"].str.strip() != ""]

            # Insertar productos
            for _, row in df.iterrows():
                nuevo_cod = generar_cod_producto(idCategoria, idSubCategoria)

                producto = Producto(
                    codProducto=nuevo_cod,
                    producto=row["producto"],
                    precioAntiguo=row.get("precioAntiguo") if not pd.isna(row.get("precioAntiguo")) else None,
                    precioNuevo=row.get("precioNuevo") if not pd.isna(row.get("precioNuevo")) else None,
                    descuento=row.get("descuento") if not pd.isna(row.get("descuento")) else None,
                    idCategoria=idCategoria,
                    idSubCategoria=idSubCategoria,
                    estado=1,
                    createdAt=datetime.now(),  # similar a GETDATE()
                    updatedAt=datetime.now()
                )
                session.add(producto)

            session.commit()
            print(f"✅ Productos insertados desde {file}")

        except Exception as e:
            session.rollback()
            print(f"❌ Error procesando {file}: {e}")

session.close()
print("🎉 Todos los productos han sido insertados en la base de datos.")
