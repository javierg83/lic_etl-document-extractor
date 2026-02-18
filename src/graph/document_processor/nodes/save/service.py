import redis
import json
import uuid
from src.config import REDIS_HOST, REDIS_PORT, REDIS_DB, REDIS_USERNAME, REDIS_PASSWORD

class SaveService:
    @staticmethod
    def save_to_redis(licitacion_id: str, filename_clean: str, file_path: str, chunks: list, 
                      licitacion_internal_id: int = None, archivo_internal_id: int = None):
        """
        Guarda los chunks vectorizados en Redis usando estructura jeraquica:
        - doc_raw:{redis_doc_id} -> Metadata Padre
        - doc_raw_page:{redis_doc_id}:p{page}... -> Contenido
        
        redis_doc_id format: <licitacion_internal_id>_<archivo_internal_id>_<filename_clean>
        Fallback (legacy): <filename_clean>
        """
        
        # Determinar el ID del documento en Redis
        if licitacion_internal_id and archivo_internal_id:
            redis_doc_id = f"{licitacion_internal_id}_{archivo_internal_id}_{filename_clean}"
        else:
            print("⚠️ [SaveService] Usando ID Legacy (filename) por falta de IDs internos.")
            redis_doc_id = filename_clean

        print(f"💾 [Nodo Save]: Guardando {len(chunks)} vectores en Redis con ID: {redis_doc_id}...")
        
        r = redis.Redis(
            host=REDIS_HOST, 
            port=REDIS_PORT, 
            db=REDIS_DB, 
            username=REDIS_USERNAME,
            password=REDIS_PASSWORD,
            decode_responses=True
        )
        
        pipeline = r.pipeline()
        
        # 1. Guardar Metadata Padre (doc_raw)
        # Calculamos total de 'páginas' viendo el max page de los chunks
        max_page = 0
        timestamp = str(uuid.uuid1()) # Placeholder de timestamp
        
        # Iterar primero para calcular max_page
        for chunk in chunks:
             meta_dict = chunk["metadata"]
             if isinstance(meta_dict, str):
                try:
                    meta_dict = json.loads(meta_dict)
                except:
                    meta_dict = {}
             p = meta_dict.get("page", 1)
             if p > max_page:
                 max_page = p
        
        parent_key = f"doc_raw:{redis_doc_id}"
        parent_data = {
            "filename": filename_clean,
            "original_path": file_path,
            "total_pages": max_page,
            "licitacion_id": licitacion_id,
            "licitacion_internal_id": str(licitacion_internal_id) if licitacion_internal_id else "",
            "archivo_internal_id": str(archivo_internal_id) if archivo_internal_id else "",
            "processed_at": timestamp,
            "status": "PROCESSED"
        }
        print(f"      -> [PARENT] {parent_key}")
        pipeline.hset(parent_key, mapping=parent_data)

        # 2. Guardar Chunks (doc_raw_page)
        for chunk in chunks:
            # Lógica de Claves según Metadata
            meta_dict = chunk["metadata"]
            if isinstance(meta_dict, str):
                try:
                    meta_dict = json.loads(meta_dict)
                except:
                    meta_dict = {}

            chunk_type = meta_dict.get("type", "unknown")
            page = meta_dict.get("page", 1)
            
            # Identificador base es el redis_doc_id
            
            if chunk_type == "element":
                # doc_raw_page:{id}:p{page}_e{elem_index}
                elem_idx = meta_dict.get("element_index", 0)
                # +1 al indice para igualar visualmente si empieza en 0
                key = f"doc_raw_page:{redis_doc_id}:p{page}_e{elem_idx+1}"
            elif chunk_type == "full_page":
                # doc_raw_page:{id}:p{page}_full
                key = f"doc_raw_page:{redis_doc_id}:p{page}_full"
            else:
                # Fallback genérico
                chunk_id = str(uuid.uuid4())[:8]
                key = f"doc_raw_page:{redis_doc_id}:p{page}_{chunk_type}_{chunk_id}"
            
            # Preparar data
            data = {
                "file_path": file_path,
                "text": chunk["text"],
                "metadata": json.dumps(meta_dict) if isinstance(meta_dict, dict) else meta_dict,
                "embedding": json.dumps(chunk.get("embedding")) if chunk.get("embedding") else "", # Ensure string
                "pagina": page,
                "tipo": str(chunk_type),
                "parent_id": parent_key
            }
            
            # print(f"      -> {key}") # Comentado para no saturar logs
            pipeline.hset(key, mapping=data)
            
        pipeline.execute()
        print("✅ Guardado exitoso en Redis.")
        
        # --- NUEVO: Encolar para extracción semántica ---
        # ELIMINADO: Ahora el BatchProcessor se encarga de notificar cuando TODOS los archivos terminan.
        # queue_msg = json.dumps({ ... })
        # r.rpush(queue_name, queue_msg)

