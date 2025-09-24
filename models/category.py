from datetime import datetime
from config.config import db

class Categoria(db.Model):
    __tablename__ = "siit_categorias"

    idCategoria = db.Column(db.Integer, primary_key=True, autoincrement=True)
    codCategoria = db.Column(db.String(256))
    categoria = db.Column(db.String(256), nullable=False)
    estado = db.Column(db.Boolean, default=True, nullable=False)

    createdAt = db.Column(db.DateTime, default=datetime.utcnow)
    updatedAt = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # relación con subcategorías
    subcategorias = db.relationship(
        "SubCategoria",
        back_populates="categoria",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Categoria {self.categoria}>"

