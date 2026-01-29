import json
import redis
import psycopg2
from psycopg2.extras import RealDictCursor
import time
import os
from src.config import (
    REDIS_HOST, REDIS_PORT, REDIS_DB, REDIS_USERNAME, REDIS_PASSWORD,
    DB_POSTGRES_NAME, DB_POSTGRES_USER, DB_POSTGRES_PASSWORD, DB_POSTGRES_HOST, DB_POSTGRES_PORT
)
from src.graph import build_simple_graph

def get_db_connection():
    return psycopg2.connect(
        dbname=DB_POSTGRES_NAME,
        user=DB_POSTGRES_USER,
        password=DB_POSTGRES_PASSWORD,
        host=DB_POSTGRES_HOST,
        port=DB_POSTGRES_PORT
    )

def process_licitacion(licitacion_id):
    print(f"🛠️ Procesando Licitación ID: {licitacion_id}")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Consultar archivos pendientes para la licitación
        # Según lic_backend/src/features/licitaciones/actions/new/service.py:84
        # La tabla es licitacion_archivos y tiene licitacion_id y nombre_archivo_org
        query = "SELECT nombre_archivo_org, ruta_almacenamiento FROM licitacion_archivos WHERE licitacion_id = %s"
        cursor.execute(query, (licitacion_id,))
        files = cursor.fetchall()
        
        conn.close()
        
        if not files:
            print(f"⚠️ No se encontraron archivos para la licitación {licitacion_id}")
            return

        print(f"📄 Archivos encontrados ({len(files)}):")
        for f in files:
            print(f"  - {f['nombre_archivo_org']}")

        # Re-construir el grafo simplificado
        app = build_simple_graph()
        
        for f in files:
            initial_state = {
                "pdf_files": [f['ruta_almacenamiento']], 
                "current_index": 0,
                "status": "init"
            }
            app.invoke(initial_state)
            
    except Exception as e:
        print(f"❌ Error procesando licitación {licitacion_id}: {e}")

def main():
    print(f"📡 Worker iniciado. Escuchando cola 'document_queue'...")
    print(f"🔗 Redis: {REDIS_HOST}:{REDIS_PORT}, DB: {REDIS_DB}")
    
    r = redis.Redis(
        host=REDIS_HOST, 
        port=REDIS_PORT, 
        db=REDIS_DB, 
        username=REDIS_USERNAME,
        password=REDIS_PASSWORD,
        decode_responses=True
    )
    
    while True:
        try:
            print("⏳ Esperando mensaje en 'document_queue'...")
            result = r.blpop("document_queue", timeout=10)
            
            if result:
                _, message = result
                print(f"📥 Mensaje recibido: {message}")
                data = json.loads(message)
                lic_id = data.get("licitacion_id")
                if lic_id:
                    process_licitacion(lic_id)
                else:
                    print("⚠️ Mensaje recibido sin licitacion_id")
            
        except redis.exceptions.ConnectionError:
            print("⚠️ Error de conexión con Redis. Reintentando en 5 segundos...")
            time.sleep(5)
        except Exception as e:
            print(f"⚠️ Error inesperado en el loop del worker: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
