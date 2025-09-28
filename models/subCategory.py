from datetime import datetime
from config.config import db

class SubCategoria(db.Model):
    __tablename__ = "siit_subcategorias"

    idSubCategoria = db.Column(db.Integer, primary_key=True, autoincrement=True)
    codSubCategoria = db.Column(db.String(256))

    idCategoria = db.Column(db.Integer, db.ForeignKey("siit_categorias.idCategoria"), nullable=False)
    subCategoria = db.Column(db.String(256), nullable=False)
    estado = db.Column(db.Boolean, default=True, nullable=False)

    createdAt = db.Column(db.DateTime, default=datetime.utcnow)
    updatedAt = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # relación inversa con categoría
    categoria = db.relationship("Categoria", back_populates="subcategorias")

    def __repr__(self):
        return f"<SubCategoria {self.subCategoria}>"