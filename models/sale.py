from config.config import db
from datetime import datetime

class Venta(db.Model):
    __tablename__ = "siit_ventas"

    idVenta = db.Column(db.Integer, primary_key=True, autoincrement=True)
    idTienda = db.Column(db.Integer, db.ForeignKey("siit_tiendas.idTienda"), nullable=False)
    idUsuario = db.Column(db.Integer, db.ForeignKey("siit_usuarios.idUsuario"), nullable=False)
    cantidadProductos = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Numeric(10,2), nullable=False)
    createdAt = db.Column(db.DateTime, default=datetime.utcnow)

    detalles = db.relationship("DetalleVenta", back_populates="venta", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Venta {self.venta}>"
