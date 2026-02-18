import os
import redis
import json
import datetime
from src.config import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD, REDIS_USERNAME, REDIS_DB

class SaveToRedisNode:
    @staticmethod
    def execute(state: dict) -> dict:
        try:
            return SaveToRedisNode._run(state)
        except Exception as e:
            state["status"] = "failed"
            state["error_node"] = "save_to_redis"
            state["error"] = str(e)
            print(f"❌ Error en SaveToRedisNode: {e}")
            return state

    @staticmethod
    def _run(state: dict) -> dict:
        chunks = state.get("chunks", [])
        embeddings = state.get("embeddings", [])
        pdf_path = state.get("current_pdf")
        filename = os.path.basename(pdf_path)
        total_pages = state.get("total_pages", 0)
        is_ocr = state.get("is_scanned", False)
        
        print(f"💾 Guardando en Redis: {filename}")
        
        r = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            password=REDIS_PASSWORD,
            username=REDIS_USERNAME,
            db=REDIS_DB,
            decode_responses=False 
        )
        
        pipe = r.pipeline()
        for i, (chunk_data, vector) in enumerate(zip(chunks, embeddings)):
            chunk_text = chunk_data["text"]
            page_num = chunk_data["page"]
            
            key = f"pdf:{filename}:chunk:{i}"
            
            metadata = {
                "source": filename,
                "page_number": page_num,
                "chapter": chunk_data.get("chapter", "Sin Sección"),
                "sub_chapter": chunk_data.get("sub_chapter", ""),
                "total_pages": total_pages,
                "chunk_index": i,
                "is_ocr": is_ocr,
                "processed_at": datetime.datetime.now().isoformat(),
                "embedding_model": "text-embedding-3-small"
            }
            
            data = {
                "text": chunk_text,
                "vector": json.dumps(vector),
                "metadata": json.dumps(metadata)
            }
            pipe.hset(key, mapping=data)
            
        pipe.execute()
        
        state["status"] = "ok"
        print(f"✅ Se guardaron {len(chunks)} fragmentos en Redis.")
        
        # --- NUEVO: Encolar para extracción semántica ---
        # Asumimos que el licitacion_id viene en el state, o usamos el filename como proxy si no está
        lic_id = state.get("licitacion_id", "SIN_LICITACION_ID") 
        # Si licitacion_id no esta definido, intentar extraer del nombre de carpeta o usar un default
        
        # El worker espera: {"licitacion_id": "...", "documento_ids": ["doc_1", ...]}
        # Aquí documento_ids es una lista de prefijos de chunks o filenames. 
        # En _load_documents_to_memory se usa el doc_id para buscar "doc_raw_page:{doc_id}:*"
        # En este nodo las keys son "pdf:{filename}:chunk:{i}". 
        # OJO: document-extractor guarda como "pdf:{filename}...", pero semantic-extractor lee "doc_raw_page:{id}..."
        # HAY UN DESAJUSTE DE KEYS.
        
        # AJUSTE TEMPORAL: Encolar mensaje. (El usuario deberá corregir keys o loader después si no coinciden)
        # Por ahora asumimos que el semantic worker sabrá qué hacer o que corregiremos el loader.
        
        queue_msg = json.dumps({
            "licitacion_id": lic_id,
            "documento_ids": [filename] 
        })
        
        print(f"🔌 [DEBUG] Conectando a Redis en: {REDIS_HOST}:{REDIS_PORT} DB={REDIS_DB}")
        
        queue_name = "semantic_queue"
        curr_len = r.llen(queue_name)
        print(f"📊 [DEBUG] Longitud cola ANTES de push: {curr_len}")
        
        r.rpush(queue_name, queue_msg)
        
        new_len = r.llen(queue_name)
        print(f"🚀 [DEBUG] Enviado a cola '{queue_name}': {queue_msg}")
        print(f"📊 [DEBUG] Longitud cola DESPUES de push: {new_len}")
        
        # Avanzar al siguiente PDF
        state["current_index"] = state.get("current_index", 0) + 1
        
        return state
