from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from config.config import db
from werkzeug.security import generate_password_hash, check_password_hash

class Cajeros(db.Model):
    __tablename__ = "siit_usuarios"
    
    idUsuario = db.Column(db.Integer, primary_key=True, autoincrement=True)
    codUsuario = db.Column(db.String(256))
    idTienda = db.Column(db.Integer, db.ForeignKey("siit_tiendas.idTienda"), nullable=False)
    
    email = db.Column(db.String(256), nullable=False)
    contrasenia = db.Column(db.String(256), nullable=False)
    
    estado = db.Column(db.Boolean, default=True, nullable=False)

    createdAt = db.Column(db.DateTime, default=datetime.utcnow)
    updatedAt = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    
    tienda = db.relationship("Store")

    def set_password(self, password):
        self.contrasenia = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.contrasenia, password)
    
    def __repr__(self):
        return f"<Cajeros {self.cajero}>"