import os
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, DECIMAL, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from config.config import Config

Base = declarative_base()

# Modelos
class Categoria(Base):
    __tablename__ = "siit_categorias"
    idCategoria = Column(Integer, primary_key=True, autoincrement=True)
    categoria = Column(String(256), nullable=False)
    subcategorias = relationship("SubCategoria", back_populates="categoria")

class SubCategoria(Base):
    __tablename__ = "siit_subCategorias"
    idSubCategoria = Column(Integer, primary_key=True, autoincrement=True)
    subCategoria = Column(String(256), nullable=False)
    idCategoria = Column(Integer, ForeignKey("siit_categorias.idCategoria"), nullable=False)
    categoria = relationship("Categoria", back_populates="subcategorias")
    productos = relationship("Producto", back_populates="subcategoria")

class Producto(Base):
    __tablename__ = "siit_productos"
    idProducto = Column(Integer, primary_key=True, autoincrement=True)
    producto = Column(String(256), nullable=False)
    precioAntiguo = Column(DECIMAL(10, 2), default=0)
    precioNuevo = Column(DECIMAL(10, 2), nullable=False)
    descuento = Column(Integer, default=0)  # porcentaje 1 a 100
    idCategoria = Column(Integer, ForeignKey("siit_categorias.idCategoria"), nullable=False)
    idSubCategoria = Column(Integer, ForeignKey("siit_subCategorias.idSubCategoria"), nullable=False)
    subcategoria = relationship("SubCategoria", back_populates="productos")

# Conexión a base de datos
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI, echo=False)
Session = sessionmaker(bind=engine)
session = Session()

# Crear tablas si no existen
Base.metadata.create_all(engine)

# Función para el procesamiento de CSV
def procesar_csv(ruta_csv):
    # Extraer ids de categoría y subcategoría del nombre del archivo
    nombre_archivo = os.path.basename(ruta_csv).replace(".csv", "")
    idCategoria, idSubCategoria = map(int, nombre_archivo.split("-"))

    # Leer CSV con pandas
    df = pd.read_csv(ruta_csv).fillna(0)

    for _, row in df.iterrows():
        producto = Producto(
            producto=row["Producto"],
            precioAntiguo=row["Precio Antiguo"] if "Precio Antiguo" in row else 0,
            precioNuevo=row["Precio Nuevo"],
            descuento=row["Descuento %"] if "Descuento %" in row else 0,
            idCategoria=idCategoria,
            idSubCategoria=idSubCategoria
        )
        session.add(producto)

    session.commit()
    print(f"✅ {len(df)} productos insertados desde {ruta_csv} (Cat {idCategoria} / Sub {idSubCategoria})")

# Constructor
if __name__ == "__main__":
    carpeta = "output"
    for archivo in os.listdir(carpeta):
        if archivo.endswith(".csv"):
            procesar_csv(os.path.join(carpeta, archivo))
