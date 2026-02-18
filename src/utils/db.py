import psycopg2
from psycopg2.extras import RealDictCursor
from src.config import (
    DB_POSTGRES_NAME, DB_POSTGRES_USER, DB_POSTGRES_PASSWORD, DB_POSTGRES_HOST, DB_POSTGRES_PORT
)

def get_db_connection():
    try:
        return psycopg2.connect(
            dbname=DB_POSTGRES_NAME,
            user=DB_POSTGRES_USER,
            password=DB_POSTGRES_PASSWORD,
            host=DB_POSTGRES_HOST,
            port=DB_POSTGRES_PORT
        )
    except Exception as e:
        print(f"❌ [CRITICAL] Fallo al conectar a DB en {DB_POSTGRES_HOST}:{DB_POSTGRES_PORT}")
        print(f"❌ Error: {e}")
        raise e

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
            SELECT la.id, la.nombre_archivo_org, la.ruta_almacenamiento, 
                   l.id_interno AS licitacion_internal_id, 
                   la.id_interno AS archivo_internal_id,
                   l.id AS licitacion_uuid
            FROM licitacion_archivos la
            JOIN licitaciones l ON la.licitacion_id = l.id
            WHERE la.licitacion_id = %s AND (UPPER(la.estado_procesamiento) = 'PENDIENTE' OR la.estado_procesamiento IS NULL)
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
