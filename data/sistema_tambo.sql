-- Base de datos: `sistema_tambo`

CREATE TABLE IF NOT EXISTS `siit_categorias` (
  `idCategoria` int NOT NULL AUTO_INCREMENT,
  `codCategoria` varchar(256) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `categoria` varchar(256) COLLATE utf8mb4_general_ci NOT NULL,
  `estado` tinyint(1) NOT NULL DEFAULT '1',
  `createdAt` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updatedAt` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`idCategoria`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS `siit_detalle_ventas` (
  `idDetalle` int NOT NULL AUTO_INCREMENT,
  `idVenta` int NOT NULL,
  `idProducto` int NOT NULL,
  `cantidad` int NOT NULL,
  `subtotal` decimal(10,2) NOT NULL,
  `createdAt` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`idDetalle`),
  KEY `idVenta` (`idVenta`),
  KEY `idProducto` (`idProducto`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS `siit_productos` (
  `idProducto` int NOT NULL AUTO_INCREMENT,
  `codProducto` varchar(256) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `producto` varchar(256) COLLATE utf8mb4_general_ci NOT NULL,
  `precioAntiguo` decimal(10,2) DEFAULT NULL,
  `precioNuevo` decimal(10,2) NOT NULL,
  `descuento` tinyint UNSIGNED DEFAULT NULL,
  `idCategoria` int NOT NULL,
  `idSubCategoria` int NOT NULL,
  `estado` tinyint(1) NOT NULL DEFAULT '1',
  `createdAt` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updatedAt` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`idProducto`),
  KEY `idCategoria` (`idCategoria`),
  KEY `idSubCategoria` (`idSubCategoria`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS `siit_productos_tiendas` (
  `id` int NOT NULL AUTO_INCREMENT,
  `idProducto` int NOT NULL,
  `idTienda` int NOT NULL,
  `stockActual` int NOT NULL DEFAULT '0',
  `stockMinimo` int NOT NULL DEFAULT '10',
  `createdAt` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updatedAt` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `siit_productos_tiendas_ibfk_1` (`idProducto`),
  KEY `siit_productos_tiendas_ibfk_2` (`idTienda`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS `siit_subcategorias` (
  `idSubCategoria` int NOT NULL AUTO_INCREMENT,
  `codSubCategoria` varchar(256) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `idCategoria` int NOT NULL,
  `subCategoria` varchar(256) COLLATE utf8mb4_general_ci NOT NULL,
  `estado` tinyint(1) NOT NULL DEFAULT '1',
  `createdAt` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updatedAt` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`idSubCategoria`),
  KEY `idCategoria` (`idCategoria`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS `siit_tiendas` (
  `idTienda` int NOT NULL AUTO_INCREMENT,
  `codTienda` varchar(256) COLLATE utf8mb4_general_ci NOT NULL,
  `tienda` varchar(256) COLLATE utf8mb4_general_ci NOT NULL,
  `ubicacion` varchar(256) COLLATE utf8mb4_general_ci NOT NULL,
  `distrito` varchar(256) COLLATE utf8mb4_general_ci NOT NULL,
  `provincia` varchar(256) COLLATE utf8mb4_general_ci NOT NULL,
  `departamento` varchar(256) COLLATE utf8mb4_general_ci NOT NULL,
  `pais` varchar(256) COLLATE utf8mb4_general_ci NOT NULL,
  `estado` tinyint(1) DEFAULT '1',
  `createdAt` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updatedAt` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`idTienda`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS `siit_usuarios` (
  `idUsuario` int NOT NULL AUTO_INCREMENT,
  `codUsuario` varchar(256) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `idTienda` int NOT NULL,
  `email` varchar(256) COLLATE utf8mb4_general_ci NOT NULL,
  `contrasenia` varchar(256) COLLATE utf8mb4_general_ci NOT NULL,
  `estado` tinyint(1) NOT NULL DEFAULT '1',
  `createdAt` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updatedAt` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`idUsuario`),
  KEY `idTienda` (`idTienda`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS `siit_ventas` (
  `idVenta` int NOT NULL AUTO_INCREMENT,
  `idTienda` int NOT NULL,
  `idUsuario` int NOT NULL,
  `cantidadProductos` int DEFAULT NULL,
  `total` decimal(10,2) NOT NULL,
  `createdAt` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`idVenta`),
  KEY `idTienda` (`idTienda`),
  KEY `idUsuario` (`idUsuario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

ALTER TABLE `siit_detalle_ventas`
  ADD CONSTRAINT `siit_detalle_ventas_ibfk_1` FOREIGN KEY (`idVenta`) REFERENCES `siit_ventas` (`idVenta`) ON DELETE CASCADE,
  ADD CONSTRAINT `siit_detalle_ventas_ibfk_2` FOREIGN KEY (`idProducto`) REFERENCES `siit_productos` (`idProducto`);

ALTER TABLE `siit_productos`
  ADD CONSTRAINT `siit_productos_ibfk_1` FOREIGN KEY (`idCategoria`) REFERENCES `siit_categorias` (`idCategoria`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `siit_productos_ibfk_2` FOREIGN KEY (`idSubCategoria`) REFERENCES `siit_subcategorias` (`idSubCategoria`) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE `siit_productos_tiendas`
  ADD CONSTRAINT `siit_productos_tiendas_ibfk_1` FOREIGN KEY (`idProducto`) REFERENCES `siit_productos` (`idProducto`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `siit_productos_tiendas_ibfk_2` FOREIGN KEY (`idTienda`) REFERENCES `siit_tiendas` (`idTienda`) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE `siit_subcategorias`
  ADD CONSTRAINT `siit_subcategorias_ibfk_1` FOREIGN KEY (`idCategoria`) REFERENCES `siit_categorias` (`idCategoria`) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE `siit_usuarios`
  ADD CONSTRAINT `siit_usuarios_ibfk_1` FOREIGN KEY (`idTienda`) REFERENCES `siit_tiendas` (`idTienda`) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE `siit_ventas`
  ADD CONSTRAINT `siit_ventas_ibfk_1` FOREIGN KEY (`idTienda`) REFERENCES `siit_tiendas` (`idTienda`) ON DELETE CASCADE,
  ADD CONSTRAINT `siit_ventas_ibfk_2` FOREIGN KEY (`idUsuario`) REFERENCES `siit_usuarios` (`idUsuario`) ON DELETE CASCADE;
COMMIT;
