import redis
import json
import uuid
from src.config import REDIS_HOST, REDIS_PORT, REDIS_DB, REDIS_USERNAME, REDIS_PASSWORD

class SaveService:
    @staticmethod
    def save_to_redis(licitacion_id: str, filename_clean: str, file_path: str, chunks: list):
        """
        Guarda los chunks vectorizados en Redis usando estructura jeraquica:
        - doc_raw:{filename} -> Metadata Padre
        - doc_raw_page:{filename}:p{page}... -> Contenido
        """
        print(f"💾 [Nodo Save]: Guardando {len(chunks)} vectores en Redis para {filename_clean}...")
        
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
        
        parent_key = f"doc_raw:{filename_clean}"
        parent_data = {
            "filename": filename_clean,
            "original_path": file_path,
            "total_pages": max_page,
            "licitacion_id": licitacion_id,
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
            
            # Identificador base es el filename_clean
            doc_id = filename_clean 
            
            if chunk_type == "element":
                # doc_raw_page:{filename}:p{page}_e{elem_index}
                elem_idx = meta_dict.get("element_index", 0)
                # +1 al indice para igualar visualmente si empieza en 0
                key = f"doc_raw_page:{doc_id}:p{page}_e{elem_idx+1}"
            elif chunk_type == "full_page":
                # doc_raw_page:{filename}:p{page}_full
                key = f"doc_raw_page:{doc_id}:p{page}_full"
            else:
                # Fallback genérico
                chunk_id = str(uuid.uuid4())[:8]
                key = f"doc_raw_page:{doc_id}:p{page}_{chunk_type}_{chunk_id}"
            
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
