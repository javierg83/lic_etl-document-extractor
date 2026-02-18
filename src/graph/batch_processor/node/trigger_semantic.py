import json
import redis
from src.config import REDIS_HOST, REDIS_PORT, REDIS_DB, REDIS_USERNAME, REDIS_PASSWORD
from src.constants.states import FileStatus

class TriggerSemanticNode:
    @staticmethod
    def execute(state: dict) -> dict:
        try:
            return TriggerSemanticNode._run(state)
        except Exception as e:
            print(f"❌ Error en TriggerSemanticNode: {e}")
            state["error_node"] = "trigger_semantic"
            state["error"] = str(e)
            return state

    @staticmethod
    def _run(state: dict) -> dict:
        licitacion_id = state.get("licitacion_id")
        processed_files = state.get("processed_files", []) # Lista de IDs de Redis
        
        if not licitacion_id:
            print("⚠️ TriggerSemanticNode: No hay licitacion_id.")
            return state
            
        if not processed_files:
            print("⚠️ TriggerSemanticNode: No se procesó ningún archivo exitosamente. No se dispara Semántico.")
            return state
            
        # Preferimos el UUID real si está disponible
        lic_uuid = state.get("licitacion_uuid")
        final_lic_id = lic_uuid if lic_uuid else licitacion_id
        
        print(f"🚀 [Batch] Preparando disparo a Semantic Queue para Licitación {final_lic_id}...")
        print(f"📊 Archivos a procesar semánticamente: {len(processed_files)}")
        
        queue_msg = json.dumps({
             "licitacion_id": final_lic_id,
             "documento_ids": processed_files
        })
        
        queue_name = "semantic_queue"
        
        try:
            r = redis.Redis(
                host=REDIS_HOST, 
                port=REDIS_PORT, 
                db=REDIS_DB, 
                username=REDIS_USERNAME,
                password=REDIS_PASSWORD,
                decode_responses=True
            )
            
            curr_len = r.llen(queue_name)
            r.rpush(queue_name, queue_msg)
            new_len = r.llen(queue_name)
            
            print(f"✅ [Batch] Mensaje enviado a '{queue_name}' (Antes: {curr_len}, Ahora: {new_len})")
            print(f"📤 Payload: {queue_msg}")
            
        except Exception as e:
            print(f"❌ Error conectando a Redis en TriggerSemanticNode: {e}")
            raise e
            
        return state
