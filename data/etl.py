# data/etl.py

import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime, date, timedelta
import os
import sys

# Ajusta el path para importar Config
# Esto asume que config/config.py está un nivel arriba del directorio data/
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from config.config import Config 

# #################################################
# CONFIGURACIÓN Y CONEXIONES
# #################################################

OLTP_DB_NAME = "sistema_tambo"
DW_DB_NAME = "data_warehouse_tambo"
LAST_RUN_DATE = '2020-01-01' # Fecha de la última ejecución exitosa del ETL

def get_last_fact_timestamp():
    query = "SELECT MAX(fecha_creacion_linea) AS last_date FROM fact_detalle_venta;"
    with dw_engine.connect() as conn:
        result = conn.execute(text(query)).fetchone()
        return result.last_date if result.last_date else date(2020, 1, 1)

def get_db_engine(db_name):
    """Crea y devuelve un engine de SQLAlchemy para la BD especificada."""
    # Reemplaza el nombre de la BD en la cadena de conexión
    conn_str = Config.SQLALCHEMY_DATABASE_URI.replace(
        f"/{Config.MYSQL_DB}", f"/{db_name}"
    )
    # El charset se asegura en la cadena de conexión
    return create_engine(conn_str)

oltp_engine = get_db_engine(OLTP_DB_NAME)
dw_engine = get_db_engine(DW_DB_NAME)

print(f"Conexión OLTP a: {OLTP_DB_NAME}")
print(f"Conexión DW a: {DW_DB_NAME}")

# #################################################
# 1. GENERACIÓN Y CARGA DE DIMENSIONES DE TIEMPO
# #################################################

def generate_dim_fecha(start_date=date(2020, 1, 1), end_date=datetime.now().date()):
    """
    Genera la Dimensión Fecha y devuelve el DataFrame,
    incluyendo un buffer de 1 año en el futuro para evitar fallas de FK.
    """
    print("-> Generando Dimensión Fecha...")
    
    # 1. DEFINIR EL RANGO FINAL CON BUFFER
    future_buffer = timedelta(days=365) # Buffer de 1 año en el futuro
    final_end_date = end_date + future_buffer
    
    # 2. GENERACIÓN
    df = pd.DataFrame({"Date": pd.date_range(start=start_date, end=final_end_date)})
    
    # ... (El resto de la lógica de la dimensión fecha queda IGUAL) ...
    df['sk_fecha'] = df['Date'].dt.strftime('%Y%m%d').astype(int)
    df['fecha'] = df['Date'].dt.date
    df['dia_del_mes'] = df['Date'].dt.day
    df['dia_de_la_semana'] = df['Date'].dt.day_name(locale='es_ES')
    df['nombre_mes'] = df['Date'].dt.strftime('%B').str.capitalize()
    df['numero_mes'] = df['Date'].dt.month
    df['trimestre'] = 'Q' + df['Date'].dt.quarter.astype(str)
    df['anio'] = df['Date'].dt.year
    df['es_fin_de_semana'] = df['Date'].dt.dayofweek.isin([5, 6]).astype(int) 
    
    return df[['sk_fecha', 'fecha', 'dia_del_mes', 'dia_de_la_semana', 'nombre_mes', 
               'numero_mes', 'trimestre', 'anio', 'es_fin_de_semana']]

def generate_dim_hora():
    """Genera la Dimensión Hora y devuelve el DataFrame."""
    print("-> Generando Dimensión Hora...")
    minutos = range(1440) 
    data = []
    for m in minutos:
        hora = m // 60
        minuto = m % 60
        sk_hora = hora * 100 + minuto
        
        # Lógica de rangos horarios
        if 6 <= hora < 12: rango = 'Mañana'
        elif 12 <= hora < 18: rango = 'Tarde'
        elif 18 <= hora < 24: rango = 'Noche'
        else: rango = 'Madrugada'
            
        data.append({
            'sk_hora': sk_hora, 'hora_24': hora, 'minuto': minuto, 'rango_horario': rango
        })
    return pd.DataFrame(data)

# data/etl.py - Función load_time_dimensions() CORREGIDA

def load_time_dimensions():
    """Carga las dimensiones de tiempo usando un enfoque de 'Insertar si no existe' (INSERT IGNORE)."""
    
    df_fecha = generate_dim_fecha()
    df_hora = generate_dim_hora()
    
    print("-> Cargando Dimensión Fecha (INSERT IGNORE)...")
    
    # 1. Carga de Dimensión Fecha
    with dw_engine.connect() as conn:
        # Usamos 'replace' en la temporal para cargar eficientemente el DataFrame
        df_fecha.to_sql('temp_dim_fecha', conn, if_exists='replace', index=False)

        # Usar INSERT IGNORE para insertar solo las SKs de fecha que no existan
        insert_ignore_sql_fecha = """
        INSERT IGNORE INTO dim_fecha (sk_fecha, fecha, dia_del_mes, dia_de_la_semana, nombre_mes, numero_mes, trimestre, anio, es_fin_de_semana)
        SELECT sk_fecha, fecha, dia_del_mes, dia_de_la_semana, nombre_mes, numero_mes, trimestre, anio, es_fin_de_semana
        FROM temp_dim_fecha;
        """
        conn.execute(text(insert_ignore_sql_fecha))
        conn.execute(text("DROP TABLE IF EXISTS temp_dim_fecha")) # Limpiar temporal
        
        conn.commit()
        
    print("Dimensión Fecha cargada/actualizada exitosamente.")
    
    # 2. Carga de Dimensión Hora
    print("-> Cargando Dimensión Hora (INSERT IGNORE)...")

    with dw_engine.connect() as conn:
        # Usamos 'replace' en la temporal
        df_hora.to_sql('temp_dim_hora', conn, if_exists='replace', index=False)

        # Usar INSERT IGNORE para insertar solo las SKs de hora que no existan
        insert_ignore_sql_hora = """
        INSERT IGNORE INTO dim_hora (sk_hora, hora_24, minuto, rango_horario)
        SELECT sk_hora, hora_24, minuto, rango_horario
        FROM temp_dim_hora;
        """
        conn.execute(text(insert_ignore_sql_hora))
        conn.execute(text("DROP TABLE IF EXISTS temp_dim_hora")) # Limpiar temporal
        
        conn.commit()

    print("Dimensión Hora cargada/actualizada exitosamente.")

# #################################################
# 2. CARGA DE DIMENSIONES DE ENTIDAD (SCD TIPO 1 - UPSERT)
# #################################################

# data/etl.py - Función genérica load_dimension CORREGIDA

# data/etl.py - Función genérica load_dimension (CORRECCIÓN V3)

def load_dimension(dim_name, query, business_key):
    """Función genérica para cargar dimensiones usando UPSERT (SCD Tipo 1)."""
    print(f"-> Extrayendo y transformando Dimensión {dim_name.capitalize()}...")
    
    # 1. EXTRACCIÓN: Obtener datos del OLTP
    df_oltp = pd.read_sql(text(query), oltp_engine)
    if df_oltp.empty:
        print(f"No hay nuevos datos para la dimensión {dim_name}.")
        return

    # 2. TRANSFORMACIÓN: Estandarización de nombres (CRÍTICA)
    
    # Paso A: Convertir a minúsculas
    df_oltp.columns = [c.lower() for c in df_oltp.columns] 
    
    # Paso B: Renombrar a snake_case para COINCIDIR con el DDL del DW
    # Detectamos y renombramos las columnas conflictivas: codtienda -> cod_tienda, codusuario -> cod_usuario, codproducto -> cod_producto
    
    renaming_map = {}
    if 'codtienda' in df_oltp.columns:
        renaming_map['codtienda'] = 'cod_tienda'
    if 'codusuario' in df_oltp.columns:
        renaming_map['codusuario'] = 'cod_usuario'
    if 'codproducto' in df_oltp.columns:
        renaming_map['codproducto'] = 'cod_producto'
        
    if renaming_map:
        df_oltp.rename(columns=renaming_map, inplace=True)
    
    # El resto del código de la función load_dimension queda igual...
    
    temp_table_name = f"temp_{dim_name}"
    
    # ... (El resto de la función: Cargar a temporal, UPSERT, Limpiar)
    with dw_engine.connect() as conn:
        # Cargar los datos nuevos o actualizados en una tabla temporal.
        df_oltp.to_sql(temp_table_name, conn, if_exists='replace', index=False) 
        
        # Generar las columnas para el INSERT (ahora usarán cod_tienda, etc.)
        cols = ', '.join([f'`{col}`' for col in df_oltp.columns])
        
        # Generar la parte de UPDATE
        bk_col_name = f'id_{business_key}_oltp'
        update_clauses = [f"`{col}` = VALUES(`{col}`)" for col in df_oltp.columns if col != bk_col_name] 
        update_clause = ', '.join(update_clauses)

        # 1. Asegurar la existencia del índice único (Clave de Negocio)
        try:
             conn.execute(text(f"CREATE UNIQUE INDEX uk_{business_key}_oltp ON {dim_name} (`{bk_col_name}`)"))
        except Exception as e:
            if 'Duplicate key name' not in str(e) and 'already exists' not in str(e):
                print(f"Advertencia al crear índice único en {dim_name}: {e}")

        # 2. SQL de UPSERT
        insert_update_sql = f"""
        INSERT INTO `{dim_name}` ({cols})
        SELECT {cols} FROM `{temp_table_name}`
        ON DUPLICATE KEY UPDATE
            {update_clause};
        """
        
        # Ejecutar la operación de UPSERT
        conn.execute(text(insert_update_sql))

        # Limpiar la tabla temporal
        conn.execute(text(f"DROP TABLE IF EXISTS `{temp_table_name}`"))
        
        conn.commit()

    print(f"Dimensión {dim_name.capitalize()} cargada/actualizada exitosamente (UPSERT - SCD T1).")
    # Fin de la función load_dimension
    """Función genérica para cargar dimensiones usando UPSERT (SCD Tipo 1)."""
    print(f"-> Extrayendo y transformando Dimensión {dim_name.capitalize()}...")
    
    # 1. EXTRACCIÓN: Obtener datos del OLTP
    df_oltp = pd.read_sql(text(query), oltp_engine)
    if df_oltp.empty:
        print(f"No hay nuevos datos para la dimensión {dim_name}.")
        return

    # 2. TRANSFORMACIÓN: Estandarización de nombres (CRÍTICA)
    
    # Paso A: Convertir a minúsculas
    df_oltp.columns = [c.lower() for c in df_oltp.columns] 
    
    # Paso B: Renombrar a snake_case para COINCIDIR con el DDL del DW
    # Detectamos y renombramos las columnas conflictivas: codtienda -> cod_tienda, codusuario -> cod_usuario, codproducto -> cod_producto
    
    renaming_map = {}
    if 'codtienda' in df_oltp.columns:
        renaming_map['codtienda'] = 'cod_tienda'
    if 'codusuario' in df_oltp.columns:
        renaming_map['codusuario'] = 'cod_usuario'
    if 'codproducto' in df_oltp.columns:
        renaming_map['codproducto'] = 'cod_producto'
        
    if renaming_map:
        df_oltp.rename(columns=renaming_map, inplace=True)
    
    # El resto del código de la función load_dimension queda igual...
    
    temp_table_name = f"temp_{dim_name}"
    
    # ... (El resto de la función: Cargar a temporal, UPSERT, Limpiar)
    with dw_engine.connect() as conn:
        # Cargar los datos nuevos o actualizados en una tabla temporal.
        df_oltp.to_sql(temp_table_name, conn, if_exists='replace', index=False) 
        
        # Generar las columnas para el INSERT (ahora usarán cod_tienda, etc.)
        cols = ', '.join([f'`{col}`' for col in df_oltp.columns])
        
        # Generar la parte de UPDATE
        bk_col_name = f'id_{business_key}_oltp'
        update_clauses = [f"`{col}` = VALUES(`{col}`)" for col in df_oltp.columns if col != bk_col_name] 
        update_clause = ', '.join(update_clauses)

        # 1. Asegurar la existencia del índice único (Clave de Negocio)
        try:
             conn.execute(text(f"CREATE UNIQUE INDEX uk_{business_key}_oltp ON {dim_name} (`{bk_col_name}`)"))
        except Exception as e:
            if 'Duplicate key name' not in str(e) and 'already exists' not in str(e):
                print(f"Advertencia al crear índice único en {dim_name}: {e}")

        # 2. SQL de UPSERT
        insert_update_sql = f"""
        INSERT INTO `{dim_name}` ({cols})
        SELECT {cols} FROM `{temp_table_name}`
        ON DUPLICATE KEY UPDATE
            {update_clause};
        """
        
        # Ejecutar la operación de UPSERT
        conn.execute(text(insert_update_sql))

        # Limpiar la tabla temporal
        conn.execute(text(f"DROP TABLE IF EXISTS `{temp_table_name}`"))
        
        conn.commit()

    print(f"Dimensión {dim_name.capitalize()} cargada/actualizada exitosamente (UPSERT - SCD T1).")
    # Fin de la función load_dimension
    """Función genérica para cargar dimensiones usando UPSERT (SCD Tipo 1)."""
    print(f"-> Extrayendo y transformando Dimensión {dim_name.capitalize()}...")
    
    # 1. EXTRACCIÓN: Obtener datos del OLTP
    df_oltp = pd.read_sql(text(query), oltp_engine)
    if df_oltp.empty:
        print(f"No hay nuevos datos para la dimensión {dim_name}.")
        return

    # 2. TRANSFORMACIÓN: Lógica de UPSERT (usando INSERT ON DUPLICATE KEY UPDATE)
    
    # Estandarizar nombres de columnas a minúsculas para consistencia con el DW
    df_oltp.columns = [c.lower() for c in df_oltp.columns] 
    
    temp_table_name = f"temp_{dim_name}"
    
    with dw_engine.connect() as conn:
        
        # Cargar los datos nuevos o actualizados en una tabla temporal.
        # *** SE ELIMINA el argumento dtype conflictivo ***
        df_oltp.to_sql(temp_table_name, conn, if_exists='replace', index=False) 
        
        # Generar las columnas para el INSERT
        cols = ', '.join([f'`{col}`' for col in df_oltp.columns])
        
        # Generar la parte de UPDATE (Actualizar todos los campos excepto la Clave de Negocio 'id_..._oltp')
        bk_col_name = f'id_{business_key}_oltp'
        # Usamos la sintaxis VALUES() de MySQL para referenciar los datos que se están insertando
        update_clauses = [f"`{col}` = VALUES(`{col}`)" for col in df_oltp.columns if col != bk_col_name] 
        update_clause = ', '.join(update_clauses)

        # 1. Asegurar la existencia del índice único (Clave de Negocio)
        try:
             conn.execute(text(f"CREATE UNIQUE INDEX uk_{business_key}_oltp ON {dim_name} (`{bk_col_name}`)"))
        except Exception as e:
            # Índice ya existe o error no crítico
            if 'Duplicate key name' not in str(e) and 'already exists' not in str(e):
                print(f"Advertencia al crear índice único en {dim_name}: {e}")

        # 2. SQL de UPSERT
        insert_update_sql = f"""
        INSERT INTO `{dim_name}` ({cols})
        SELECT {cols} FROM `{temp_table_name}`
        ON DUPLICATE KEY UPDATE
            {update_clause};
        """
        
        # Ejecutar la operación de UPSERT
        conn.execute(text(insert_update_sql))

        # Limpiar la tabla temporal
        conn.execute(text(f"DROP TABLE IF EXISTS `{temp_table_name}`"))
        
        conn.commit()

    print(f"Dimensión {dim_name.capitalize()} cargada/actualizada exitosamente (UPSERT - SCD T1).")


# Consultas Específicas para Dimensiones

PRODUCT_QUERY = """
SELECT
    p.idProducto AS id_producto_oltp,
    p.codProducto AS cod_producto,
    p.producto AS nombre_producto,
    p.precioNuevo AS precio_nuevo_actual,
    p.descuento,
    c.categoria,
    s.subCategoria AS subcategoria
FROM 
    siit_productos p
JOIN 
    siit_categorias c ON p.idCategoria = c.idCategoria
JOIN 
    siit_subcategorias s ON p.idSubCategoria = s.idSubCategoria;
"""

TIENDA_QUERY = """
SELECT
    idTienda AS id_tienda_oltp,
    codTienda AS cod_tienda,
    tienda AS nombre_tienda,
    ubicacion,
    distrito,
    provincia,
    departamento,
    pais
FROM 
    siit_tiendas;
"""

USUARIO_QUERY = """
SELECT
    idUsuario AS id_usuario_oltp,
    codUsuario AS cod_usuario,
    email
FROM 
    siit_usuarios;
"""

def load_product_dimension():
    load_dimension('dim_producto', PRODUCT_QUERY, 'producto')

def load_tienda_dimension():
    load_dimension('dim_tienda', TIENDA_QUERY, 'tienda')

def load_usuario_dimension():
    load_dimension('dim_usuario', USUARIO_QUERY, 'usuario')


# #################################################
# 3. CARGA DE LA TABLA DE HECHOS (FACT TABLE)
# #################################################

def get_dimension_maps(dw_engine):
    """Extrae los mapeos de Clave Natural (OLTP) a Clave Subrogada (DW)."""
    print("-> Extrayendo mapeos de claves del DW...")
    
    # Mapeo de Producto: id_producto_oltp -> sk_producto
    df_map_prod = pd.read_sql_table('dim_producto', dw_engine, 
                                    columns=['id_producto_oltp', 'sk_producto'])
    map_producto = df_map_prod.set_index('id_producto_oltp')['sk_producto'].to_dict()
    
    # Mapeo de Tienda: id_tienda_oltp -> sk_tienda
    df_map_tienda = pd.read_sql_table('dim_tienda', dw_engine, 
                                      columns=['id_tienda_oltp', 'sk_tienda'])
    map_tienda = df_map_tienda.set_index('id_tienda_oltp')['sk_tienda'].to_dict()
    
    # Mapeo de Usuario: id_usuario_oltp -> sk_usuario
    df_map_usuario = pd.read_sql_table('dim_usuario', dw_engine, 
                                       columns=['id_usuario_oltp', 'sk_usuario'])
    map_usuario = df_map_usuario.set_index('id_usuario_oltp')['sk_usuario'].to_dict()
    
    return {
        'producto': map_producto,
        'tienda': map_tienda, 
        'usuario': map_usuario 
    }

def load_fact_detalle_venta(dimension_maps):
    print("-> Extrayendo y transformando Tabla de Hechos...")

    last_run_date = get_last_fact_timestamp()
    print(f"Última fecha cargada en DW: {last_run_date}")

    query = f"""
    SELECT
        dv.idVenta AS id_venta_oltp,
        dv.idProducto AS id_producto_oltp,
        v.idTienda AS id_tienda_oltp,
        v.idUsuario AS id_usuario_oltp,
        dv.cantidad AS cantidad_vendida,
        dv.subtotal,
        v.createdAt
    FROM 
        siit_detalle_ventas dv
    JOIN 
        siit_ventas v ON dv.idVenta = v.idVenta
    WHERE 
        v.createdAt > '{last_run_date}';
    """

    df_fact = pd.read_sql(text(query), oltp_engine)

    if df_fact.empty:
        print("No se encontraron nuevos registros de ventas para cargar.")
        return

    print(f"Registros de hechos extraídos: {len(df_fact)}")

    df_fact['precio_venta_unitario'] = df_fact.apply(
        lambda row: round(row['subtotal'] / row['cantidad_vendida'], 2) 
        if row['cantidad_vendida'] > 0 else 0, axis=1
    )
    
    df_fact['fk_fecha'] = pd.to_datetime(df_fact['createdAt']).dt.strftime('%Y%m%d').astype(int)
    df_fact['fk_hora'] = pd.to_datetime(df_fact['createdAt']).dt.strftime('%H%M').astype(int)
    df_fact['fecha_creacion_linea'] = df_fact['createdAt']
    
    df_fact['fk_producto'] = df_fact['id_producto_oltp'].map(dimension_maps['producto'])
    df_fact['fk_tienda'] = df_fact['id_tienda_oltp'].map(dimension_maps['tienda'])
    df_fact['fk_usuario'] = df_fact['id_usuario_oltp'].map(dimension_maps['usuario'])

    df_fact.rename(columns={'subtotal': 'subtotal_linea'}, inplace=True)

    df_fact.dropna(subset=['fk_producto', 'fk_tienda', 'fk_usuario'], inplace=True)

    fact_columns = [
        'id_venta_oltp', 'fk_producto', 'fk_tienda', 'fk_usuario', 
        'fk_fecha', 'fk_hora', 'cantidad_vendida', 
        'precio_venta_unitario', 'subtotal_linea', 'fecha_creacion_linea'
    ]

    # 🔥 INSERT IGNORE PARA EVITAR DUPLICADOS 🔥
    with dw_engine.connect() as conn:
        df_fact[fact_columns].to_sql('temp_fact', conn, if_exists='replace', index=False)

        sql = """
        INSERT IGNORE INTO fact_detalle_venta
        SELECT * FROM temp_fact;
        """

        conn.execute(text(sql))
        conn.execute(text("DROP TABLE temp_fact"))
        conn.commit()

    print(f"Tabla de Hechos cargada exitosamente. Filas insertadas: {len(df_fact)}")

# #################################################
# 5. FUNCIÓN PRINCIPAL DE ETL
# #################################################

def run_etl():
    """Ejecuta el proceso ETL completo."""
    print("\n--- INICIO DEL PROCESO ETL TAMBO (Modo Producción) ---")
    try:
        # 1. Carga de Dimensiones de Tiempo (Estáticas)
        load_time_dimensions()
        
        # 2. Carga de Dimensiones de Entidad (UPSERT - SCD T1)
        load_tienda_dimension()
        load_usuario_dimension()
        load_product_dimension()
        
        # 3. Obtener Mapeos de Claves Subrogadas (Necesario ANTES de cargar Hechos)
        dimension_maps = get_dimension_maps(dw_engine)
        
        # 4. Carga de la Tabla de Hechos (APPEND)
        load_fact_detalle_venta(dimension_maps)

    except Exception as e:
        print(f"\n!!! ERROR CRÍTICO EN EL PROCESO ETL: {e} !!!")
        print("La carga ha sido detenida.")
        
    print("--- FIN DEL PROCESO ETL TAMBO ---")

if __name__ == '__main__':
    # Asegúrate de que tu .env y config.py estén correctamente configurados
    run_etl()