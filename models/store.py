from config.config import db

class Store(db.Model):
    __tablename__ = "siit_tiendas"

    idTienda = db.Column(db.Integer, primary_key=True, autoincrement=True)
    codTienda = db.Column(db.String(256), nullable=False)
    tienda = db.Column(db.String(256), nullable=False)
    ubicacion = db.Column(db.String(256), nullable=False)
    distrito = db.Column(db.String(256), nullable=False)
    provincia = db.Column(db.String(256), nullable=False)
    departamento = db.Column(db.String(256), nullable=False)
    pais = db.Column(db.String(256), nullable=False)
    estado = db.Column(db.Boolean, default=True)
    createdAt = db.Column(db.DateTime)
    updatedAt = db.Column(db.DateTime)

    def __repr__(self):
        return f"<Store {self.nombre}>"
