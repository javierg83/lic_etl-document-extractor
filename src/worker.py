import json
import redis
import time
import os
from src.config import (
    REDIS_HOST, REDIS_PORT, REDIS_DB, REDIS_USERNAME, REDIS_PASSWORD
)
from src.graph.batch_processor.graph import build_batch_processor

from src.utils.db import get_db_connection

def process_licitacion(licitacion_id):
    print(f"🛠️ Procesando Licitación ID: {licitacion_id}")
    
    try:
        # Usar el nuevo Batch Processor
        app = build_batch_processor()
        
        initial_state = {
            "licitacion_id": licitacion_id,
            "current_index": 0,
            "status": "init"
        }
        
        # Ejecutar orquestador del lote
        # Ahora el grafo se encarga de buscar los archivos y actualizar estados en DB
        final_state = app.invoke(initial_state)
        
        print("\n📊 Resumen final del lote:")
        for file, status in final_state.get("file_states", {}).items():
            print(f"  - {os.path.basename(file)}: {status}")
            
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

    # --- TEMPORAL: Verificación de conexión al inicio ---
    try:
        print("🔍 Verificando conexión inicial con Redis...")
        r.ping()
        print("✅ Conexión inicial exitosa.")
    except redis.exceptions.AuthenticationError:
        print("❌ Error Fatal: Contraseña de Redis incorrecta.")
        return
    except Exception as e:
        print(f"❌ Error Fatal: No se pudo conectar a Redis al inicio ({e})")
        return
    # ----------------------------------------------------
    
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
