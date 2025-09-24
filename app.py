from flask import Flask, redirect, url_for
from config.config import Config
from config.config import db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    from routes.admin import admin_bp
    from routes.stores import stores_bp
    from routes.products import productos_bp
    from routes.cashiers import cajeros_bp
    from routes.sales import sales_bp
    from routes.stock import stock_bp
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(stores_bp, url_prefix="/stores")
    app.register_blueprint(productos_bp, url_prefix="/products")
    app.register_blueprint(cajeros_bp, url_prefix="/cashiers")
    app.register_blueprint(sales_bp, url_prefix="/sales")
    app.register_blueprint(stock_bp, url_prefix="/stock")
    return app

    
app = create_app()

@app.route("/")
def home():
    return redirect(url_for("admin.dashboard"))

if __name__ == "__main__":
    app.run(debug=True)
