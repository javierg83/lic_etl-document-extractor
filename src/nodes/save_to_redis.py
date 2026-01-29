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
        
        # Avanzar al siguiente PDF
        state["current_index"] = state.get("current_index", 0) + 1
        
        return state
