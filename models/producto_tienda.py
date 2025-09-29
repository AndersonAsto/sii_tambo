# models/producto_tienda.py
from config.config import db

class ProductoTienda(db.Model):
    __tablename__ = "siit_productos_tiendas"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    idProducto = db.Column(db.Integer, db.ForeignKey("siit_productos.idProducto"), nullable=False)
    idTienda = db.Column(db.Integer, db.ForeignKey("siit_tiendas.idTienda"), nullable=False)
    stockActual = db.Column(db.Integer, default=0)
    stockMinimo = db.Column(db.Integer, default=10)
    createdAt = db.Column(db.DateTime)
    updatedAt = db.Column(db.DateTime)

    # relaciones para facilitar templates
    producto = db.relationship("Producto", backref="productos_tiendas", lazy="joined")
    tienda = db.relationship("Store", backref="productos_tiendas", lazy="joined")

    def __repr__(self):
        return f"<ProductoTienda prod={self.idProducto} tienda={self.idTienda} stock={self.stockActual}>"