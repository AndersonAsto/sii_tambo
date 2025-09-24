import pandas as pd
from config.config import Config, db
from models.store import Store
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func

# Crear motor y sesión
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=engine)
session = Session()

# Leer CSV
df = pd.read_csv("data/tiendas.csv")

def generar_codigo(departamento, provincia, distrito):
    # Tomar las primeras 3 letras en mayúsculas
    dep = departamento.strip().upper()[:3]
    prov = provincia.strip().upper()[:3]
    dist = distrito.strip().upper()[:3]

    prefijo = f"{dep}{prov}{dist}"

    # Buscar último código existente con ese prefijo
    ultimo = (
        session.query(Store)
        .filter(Store.codTienda.like(f"{prefijo}%"))
        .order_by(Store.codTienda.desc())
        .first()
    )

    if ultimo:
        # Extraer el número al final del código y sumarle 1
        num = int(ultimo.codTienda[-4:]) + 1
    else:
        num = 1

    return f"{prefijo}{num:04d}"


# Insertar filas del CSV
for _, row in df.iterrows():
    cod_tienda = generar_codigo(row["departamento"], row["provincia"], row["distrito"])

    nueva_tienda = Store(
        codTienda=cod_tienda,
        tienda=row["tienda"],
        ubicacion=row["ubicacion"],
        distrito=row["distrito"],
        provincia=row["provincia"],
        departamento=row["departamento"],
        pais=row["pais"]
    )

    session.add(nueva_tienda)

# Confirmar cambios
session.commit()
session.close()

print("✅ Tiendas insertadas correctamente en la base de datos con códigos personalizados.")
