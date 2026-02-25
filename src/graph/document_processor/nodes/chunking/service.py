from langchain_text_splitters import RecursiveCharacterTextSplitter

class ChunkingService:
    @staticmethod
    def chunk_text(pages_content: list, chunk_size=1000, chunk_overlap=200) -> list:
        """
        Recibe lista de páginas con texto y retorna lista de chunks (Document objects o dicts).
        """
        print(f"✂️ [Nodo Chunking]: Chunking {len(pages_content)} páginas (Legacy Text Splitter)...")
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", " ", ""]
        )
        
        all_chunks = []
        
        for page_data in pages_content:
            text = page_data.get("text", "")
            page_num = page_data.get("page", 0)
            
            if not text.strip():
                continue
                
            # 1. Crear chunk de página completa (Full Page)
            full_page_metadata = {
                "page": page_num,
                "sheet_name": page_data.get("sheet_name"),
                "origin": "standard",
                "type": "full_page"
            }
            all_chunks.append({
                "text": text,
                "metadata": full_page_metadata
            })
            
            # 2. Crear chunks individuales con el Text Splitter
            # Se usa un solo metadato base inicialmente
            base_metadata = {
                "page": page_num, 
                "sheet_name": page_data.get("sheet_name"),
                "origin": "standard"
            }
            
            chunks = text_splitter.create_documents([text], metadatas=[base_metadata])
            
            # Convertimos a formato serializable e inyectamos type y element_index
            for idx, chunk in enumerate(chunks):
                # Clonar metadata base para no mutar el mismo dict en caso de que langchain lo re-use
                chunk_meta = dict(chunk.metadata)
                chunk_meta["type"] = "element"
                chunk_meta["element_index"] = idx # Base 0 para que save_service al hacer +1 coincida visualmente
                
                all_chunks.append({
                    "text": chunk.page_content,
                    "metadata": chunk_meta
                })
                
        return all_chunks

    @staticmethod
    def process_structured_elements(elements: list) -> list:
        """
        Procesa elementos estructurados (OCR Vision) y genera:
        1. Chunks por elemento individual.
        2. Chunks de página completa (concatenados).
        """
        print(f"🧩 [Nodo Chunking]: Procesando {len(elements)} elementos estructurados...")
        chunks = []
        
        # Contador auxiliar de elementos por página en caso de que falte element_index
        from collections import defaultdict
        page_element_counters = defaultdict(int)
        
        # 1. Chunks por elemento
        for el in elements:
            content = el.get("contenido", "")
            page_num = el.get("pagina", 0)
            
            # Si es lista (tabla), convertir a string
            if isinstance(content, list):
                import json
                text = json.dumps(content, ensure_ascii=False)
            else:
                text = str(content)
            
            if not text.strip():
                continue
                
            # Obtener index original asignado por OCR, si no existe calculamos uno usando el contador local
            el_idx = el.get("element_index")
            if el_idx is None:
                el_idx = page_element_counters[page_num]
            
            metadata = {
                "doc_id": el.get("doc_id"), # Debería venir del state si es necesario, o del elemento
                "page": page_num,
                "type": "element",
                "original_type": el.get("type"),
                "element_index": el_idx
            }
            
            chunks.append({
                "text": text,
                "metadata": metadata
            })
            
            # Incrementar el contador asignado
            page_element_counters[page_num] += 1
            
        # 2. Chunks Full Page (agrupando por página)
        pages_text = defaultdict(list)
        
        for el in elements:
            page = el.get("pagina")
            content = el.get("contenido", "")
            if isinstance(content, list):
                import json
                text = json.dumps(content, ensure_ascii=False)
            else:
                text = str(content)
            pages_text[page].append(text)
            
        for page_num, texts in pages_text.items():
            full_text = "\n".join(texts)
            if full_text.strip():
                metadata = {
                    "page": page_num,
                    "type": "full_page"
                }
                chunks.append({
                    "text": full_text,
                    "metadata": metadata
                })
        
        print(f"   🧩 Resumen de Chunks Generados:")
        print(f"      - Elementos individuales: {len(chunks) - len(pages_text)}")
        print(f"      - Páginas completas: {len(pages_text)}")
        print(f"      - Total: {len(chunks)}")
        
        return chunks
