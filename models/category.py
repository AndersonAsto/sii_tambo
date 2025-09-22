from config.config import db

class Category(db.Model):
    __tablename__ = "siit_categorias"

    idCategoria = db.Column(db.Integer, primary_key=True, autoincrement=True)
    codCategoria = db.Column(db.String(256))
    categoria = db.Column(db.String(256), nullable=False)
    estado = db.Column(db.Boolean, default=True, nullable=False)
    createdAt = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())
    updatedAt = db.Column(
        db.TIMESTAMP,
        server_default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp(),
    )

    # Relaciones
    productos = db.relationship("Producto", back_populates="categoria", cascade="all, delete-orphan")
    subcategorias = db.relationship("SubCategoria", back_populates="categoria", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Category {self.categoria}>"
