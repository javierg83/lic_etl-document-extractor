import psycopg2
from psycopg2.extras import RealDictCursor
from src.config import (
    DB_POSTGRES_NAME, DB_POSTGRES_USER, DB_POSTGRES_PASSWORD, DB_POSTGRES_HOST, DB_POSTGRES_PORT
)

def get_db_connection():
    return psycopg2.connect(
        dbname=DB_POSTGRES_NAME,
        user=DB_POSTGRES_USER,
        password=DB_POSTGRES_PASSWORD,
        host=DB_POSTGRES_HOST,
        port=DB_POSTGRES_PORT
    )

def get_pending_files(licitacion_id: int):
    """
    Obtiene los archivos con estado 'pendiente' para una licitación dada.
    Se asume que la tabla es 'licitacion_archivos' y tiene las columnas 
    'id', 'nombre_archivo_org' y 'ruta_almacenamiento'.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        query = """
            SELECT id, nombre_archivo_org, ruta_almacenamiento 
            FROM licitacion_archivos 
            WHERE licitacion_id = %s AND (UPPER(estado_procesamiento) = 'PENDIENTE' OR estado_procesamiento IS NULL)
        """
        cursor.execute(query, (licitacion_id,))
        return cursor.fetchall()
    finally:
        conn.close()

def change_status(archivo_id: int, status: str):
    """
    Cambia el estado de un archivo en la base de datos y actualiza la fecha de procesado.
    """
    status_upper = status.upper()
    print(f"🗄️ [DB] Cambiando estado de archivo {archivo_id} a '{status_upper}'")
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        query = """
            UPDATE licitacion_archivos 
            SET estado_procesamiento = %s, 
                fecha_procesado = NOW() 
            WHERE id = %s
        """
        cursor.execute(query, (status_upper, archivo_id))
        conn.commit()
    finally:
        conn.close()
