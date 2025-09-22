from flask import Flask, redirect, url_for
from config.config import Config
from config.config import db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    from routes.admin import admin_bp
    from routes.stores import stores_bp
    from routes.prod import productos_bp
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(stores_bp, url_prefix="/stores")
    app.register_blueprint(productos_bp, url_prefix="/products")
    return app

    
app = create_app()

@app.route("/")
def home():
    return redirect(url_for("admin.dashboard"))

if __name__ == "__main__":
    app.run(debug=True)
