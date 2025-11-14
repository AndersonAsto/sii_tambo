create table siit_tiendas(
    idTienda INT AUTO_INCREMENT PRIMARY KEY,
    nombreTienda VARCHAR(256) NOT NULL,
    ubicacionTienda VARCHAR(256) NOT NULL,
    distrito VARCHAR(256) NOT NULL,
    provincia VARCHAR(256) NOT NULL,
    departamento VARCHAR(256) NOT NULL,
    pais VARCHAR(256) NOT NULL
)

CREATE TABLE siit_categorias(
    idCategoria INT AUTO_INCREMENT PRIMARY KEY,
    codCategoria VARCHAR(256),
    categoria VARCHAR(256) NOT NULL,
    estado TINYINT(1) NOT NULL DEFAULT 1,
    createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
)

CREATE TABLE siit_subCategorias(
    idCategoria INT AUTO_INCREMENT PRIMARY KEY,
    codSubCategoria VARCHAR(256),
    subCategoria VARCHAR(256) NOT NULL,
    estado TINYINT(1) NOT NULL DEFAULT 1,
    createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
)

CREATE TABLE siit_productos (
    idProducto INT AUTO_INCREMENT PRIMARY KEY,
    producto VARCHAR(256) NOT NULL,         -- nombre del producto
    precioAntiguo DECIMAL(10,2) NULL,      -- hasta 2 decimales
    precioNuevo DECIMAL(10,2) NOT NULL,    -- hasta 2 decimales
    descuento TINYINT UNSIGNED NULL,       -- porcentaje 1 a 100
    idCategoria INT NOT NULL,
    idSubCategoria INT NOT NULL,
    estado TINYINT(1) NOT NULL DEFAULT 1,
    createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_producto_categoria FOREIGN KEY (idCategoria) 
        REFERENCES siit_categorias(idCategoria)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_producto_subcategoria FOREIGN KEY (idSubCategoria) 
        REFERENCES siit_subCategorias(idSubCategoria)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);