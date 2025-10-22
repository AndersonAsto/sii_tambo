from config.config import db
from models.category import Categoria


class Producto(db.Model):
    __tablename__ = 'siit_productos'

    idProducto = db.Column(db.Integer, primary_key=True, autoincrement=True)
    codProducto = db.Column(db.String(256))
    producto = db.Column(db.String(256), nullable=False)
    precioAntiguo = db.Column(db.Numeric(10,2))
    precioNuevo = db.Column(db.Numeric(10,2), nullable=False)
    descuento = db.Column(db.SmallInteger, nullable=True)
    idCategoria = db.Column(db.Integer, nullable=False)
    idSubCategoria = db.Column(db.Integer, nullable=False)
    estado = db.Column(db.Boolean, default=True)
    createdAt = db.Column(db.DateTime)
    updatedAt = db.Column(db.DateTime)
    

    def __repr__(self):
        return f"<Producto {self.producto}>"
