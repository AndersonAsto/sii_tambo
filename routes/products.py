from flask import Blueprint, render_template, request
from models.products import Producto
from models.category import Categoria
from models.subCategory import SubCategoria

productos_bp = Blueprint('productos', __name__)

@productos_bp.route("/productos")
def productos():
    # Obtener filtros desde la URL
    categoria_id = request.args.get("categoria", type=int)
    subcategoria_id = request.args.get("subcategoria", type=int)
    page = request.args.get("page", 1, type=int)
    per_page = 25  # paginación de 25 productos

    # Query base
    query = Producto.query

    # Aplicar filtros si existen
    if categoria_id:
        query = query.filter(Producto.idCategoria == categoria_id)
    if subcategoria_id:
        query = query.filter(Producto.idSubCategoria == subcategoria_id)

    # Paginación
    productos_paginados = query.paginate(page=page, per_page=per_page, error_out=False)

    # Cargar todas las categorías para el filtro
    categorias = Categoria.query.all()

    # Si hay categoría seleccionada, cargamos subcategorías correspondientes
    subcategorias = []
    if categoria_id:
        subcategorias = SubCategoria.query.filter_by(idCategoria=categoria_id).all()

    return render_template(
        "producto.html",
        productos=productos_paginados.items,
        pagination=productos_paginados,
        categoria_id=categoria_id,
        subcategoria_id=subcategoria_id,
        categorias=categorias,
        subcategorias=subcategorias
    )
    