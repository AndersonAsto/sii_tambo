import mysql.connector
from datetime import datetime
from werkzeug.security import generate_password_hash

# ===========================
# CONFIGURACIÓN DE CONEXIÓN
# ===========================
conexion = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="sistema_tambo"
)

cursor = conexion.cursor(dictionary=True)

# ===========================
# 1️⃣ LEER TIENDAS
# ===========================
cursor.execute("SELECT idTienda, codTienda FROM siit_tiendas;")
tiendas = cursor.fetchall()

# ===========================
# 2️⃣ GENERAR USUARIOS
# ===========================
usuarios = []
fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

for tienda in tiendas:
    id_tienda = tienda["idTienda"]
    cod_tienda = tienda["codTienda"]
    
    # Generar código y correo
    cod_usuario = f"USR{str(id_tienda).zfill(3)}"
    email = f"{cod_tienda.lower()}@gmail.com"
    
    # Cifrar contraseña "123456" con scrypt
    contrasenia_hash = generate_password_hash("123456", method="scrypt")
    
    usuarios.append((
        cod_usuario,
        id_tienda,
        email,
        contrasenia_hash,
        1,  # estado
        fecha_actual,
        fecha_actual
    ))

# ===========================
# 3️⃣ INSERTAR EN LA BASE DE DATOS
# ===========================
sql_insert = """
INSERT INTO siit_usuarios (codUsuario, idTienda, email, contrasenia, estado, createdAt, updatedAt)
VALUES (%s, %s, %s, %s, %s, %s, %s)
"""

cursor.executemany(sql_insert, usuarios)
conexion.commit()

print(f"✅ Se insertaron {len(usuarios)} usuarios correctamente.")

# ===========================
# CERRAR CONEXIÓN
# ===========================
cursor.close()
conexion.close()
