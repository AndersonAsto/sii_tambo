from config.config import db

class SubCategory(db.Model):
    __tablename__ = "siit_subcategorias"

    idSubCategoria = db.Column(db.Integer, primary_key=True, autoincrement=True)
    codSubCategoria = db.Column(db.String(256))
    subCategoria = db.Column(db.String(256), nullable=False)
    estado = db.Column(db.Boolean, default=True, nullable=False)
    createdAt = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())
    updatedAt = db.Column(
        db.TIMESTAMP,
        server_default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp(),
    )

    # Relaciones
    productos = db.relationship("Producto", back_populates="subcategoria", cascade="all, delete-orphan")
    categoria_id = db.Column(db.Integer, db.ForeignKey("siit_categorias.idCategoria", ondelete="CASCADE", onupdate="CASCADE"))
    categoria = db.relationship("Categoria", back_populates="subcategorias")

    def __repr__(self):
        return f"<SubCategory {self.subCategoria}>"
