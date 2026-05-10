"""
Configuracion de conexion a PostgreSQL (Supabase).
Lee las credenciales desde el archivo .env
"""

import os
import psycopg2
from dotenv import load_dotenv

# Cargar variables desde .env (busca en el directorio del script)
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "database": os.getenv("DB_NAME", "postgres"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD"),
}


def get_connection():
    """Crea y retorna una conexion a PostgreSQL."""
    return psycopg2.connect(**DB_CONFIG)


def init_table():
    """Crea la tabla datos_warehouse si no existe."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS datos_warehouse (
            id SERIAL PRIMARY KEY,
            origen VARCHAR(10) NOT NULL,
            contenido TEXT NOT NULL,
            fecha TIMESTAMP DEFAULT NOW()
        );
    """)
    conn.commit()
    cur.close()
    conn.close()
    print("[DB] Tabla datos_warehouse verificada/creada.")


def insertar_dato(origen, contenido):
    """Inserta un registro en la tabla datos_warehouse."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO datos_warehouse (origen, contenido) VALUES (%s, %s)",
        (origen, contenido),
    )
    conn.commit()
    cur.close()
    conn.close()


if __name__ == "__main__":
    # Prueba rapida de conexion
    try:
        conn = get_connection()
        print("[DB] Conexion exitosa a Supabase.")
        conn.close()
        init_table()
        print("[DB] Todo listo.")
    except Exception as e:
        print(f"[DB] Error de conexion: {e}")
