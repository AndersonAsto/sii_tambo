from config.config import db

class Products(db.Model):
    __tablename__ = "siit_productos2"

    idProducto = db.Column(db.Integer, primary_key=True, autoincrement=True)
    producto = db.Column(db.String(256), nullable=False)
    precioAntiguo = db.Column(db.Numeric(10, 2))
    precioNuevo = db.Column(db.Numeric(10, 2), nullable=False)
    descuento = db.Column(db.Integer, default=0)
    estado = db.Column(db.Boolean, default=True, nullable=False)
    createdAt = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())
    updatedAt = db.Column(
        db.TIMESTAMP,
        server_default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp(),
    )

    # FK
    idCategoria = db.Column(db.Integer, db.ForeignKey("siit_categorias.idCategoria", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    idSubCategoria = db.Column(db.Integer, db.ForeignKey("siit_subcategorias.idSubCategoria", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)

    # Relaciones
    categoria = db.relationship("Categoria", back_populates="productos")
    subcategoria = db.relationship("SubCategoria", back_populates="productos")

    def __repr__(self):
        return f"<Products {self.producto} - {self.precioNuevo}>"
