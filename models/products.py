from config.config import db

class Producto(db.Model):
    __tablename__ = 'siit_productos'

    idProducto = db.Column(db.Integer, primary_key=True)
    producto = db.Column(db.String(256))
    precioAntiguo = db.Column(db.Numeric(10, 2))
    precioNuevo = db.Column(db.Numeric(10, 2))
    descuento = db.Column(db.Integer)  # tinyint en la BD → mejor Integer
    idCategoria = db.Column(db.Integer)  # estaba en la tabla pero faltaba en el modelo
    idSubCategoria = db.Column(db.Integer)
    estado = db.Column(db.Boolean)  # tinyint(1) → Boolean en SQLAlchemy
    createdAt = db.Column(db.DateTime)  # corregido nombre
    updatedAt = db.Column(db.DateTime)  # corregido nombre

    def __repr__(self):
        return f"<Producto {self.producto}>"
