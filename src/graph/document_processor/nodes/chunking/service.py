from langchain_text_splitters import RecursiveCharacterTextSplitter

class ChunkingService:
    @staticmethod
    def chunk_text(pages_content: list, chunk_size=1000, chunk_overlap=200) -> list:
        """
        Recibe lista de páginas con texto y retorna lista de chunks (Document objects o dicts).
        """
        print(f"✂️ [Nodo Chunking]: Chunking {len(pages_content)} páginas...")
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", " ", ""]
        )
        
        all_chunks = []
        
        for page_data in pages_content:
            text = page_data.get("text", "")
            page_num = page_data.get("page", 0)
            
            # Si es Excel o Word, 'page' podría ser sheet_name o similar, se maneja igual como metadato
            metadata = {
                "page": page_num, 
                "sheet_name": page_data.get("sheet_name"),
                "origin": "standard" # O pasarlo como argumento
            }
            
            chunks = text_splitter.create_documents([text], metadatas=[metadata])
            
            # Convertimos a formato serializable si queremos guadar en state simple
            for chunk in chunks:
                all_chunks.append({
                    "text": chunk.page_content,
                    "metadata": chunk.metadata
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
        
        # 1. Chunks por elemento
        for el in elements:
            content = el.get("contenido", "")
            # Si es lista (tabla), convertir a string
            if isinstance(content, list):
                import json
                text = json.dumps(content, ensure_ascii=False)
            else:
                text = str(content)
            
            if not text.strip():
                continue
                
            metadata = {
                "doc_id": el.get("doc_id"), # Debería venir del state si es necesario, o del elemento
                "page": el.get("pagina"),
                "type": "element",
                "original_type": el.get("type"),
                "element_index": el.get("element_index")
            }
            
            chunks.append({
                "text": text,
                "metadata": metadata
            })
            
        # 2. Chunks Full Page (agrupando por página)
        from collections import defaultdict
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
