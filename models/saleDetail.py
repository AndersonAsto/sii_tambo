from config.config import db
from datetime import datetime

class DetalleVenta(db.Model):
    __tablename__ = "siit_detalle_ventas"

    idDetalle = db.Column(db.Integer, primary_key=True, autoincrement=True)
    idVenta = db.Column(db.Integer, db.ForeignKey("siit_ventas.idVenta"), nullable=False)
    idProducto = db.Column(db.Integer, db.ForeignKey("siit_productos.idProducto"), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    subtotal = db.Column(db.Numeric(10,2), nullable=False)
    createdAt = db.Column(db.DateTime, default=datetime.utcnow)

    venta = db.relationship("Venta", back_populates="detalles")
    producto = db.relationship("Producto")

    def __repr__(self):
        return f"<DetalleVenta {self.idDetalle}>"