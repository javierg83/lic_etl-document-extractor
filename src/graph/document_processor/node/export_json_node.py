import os
import json
import datetime

class ExportToJsonNode:
    """
    Nodo de utilidad para DEV. 
    Exporta los chunks y metadatos a archivos JSON organizados por carpeta y página.
    """
    @staticmethod
    def execute(state: dict) -> dict:
        """
        Orquestador del nodo.
        Maneja errores y garantiza que el grafo reciba un state consistente.
        """
        try:
            return ExportToJsonNode._run(state)
        except Exception as e:
            state["status"] = "failed"
            state["error_node"] = "export_json"
            state["error"] = str(e)
            print(f"❌ Error en ExportToJsonNode: {e}")
            return state

    @staticmethod
    def _run(state: dict) -> dict:
        chunks = state.get("chunks", [])
        pdf_path = state.get("current_pdf")
        filename = os.path.basename(pdf_path)
        pdf_dir = os.path.dirname(pdf_path)
        total_pages = state.get("total_pages", 0)
        is_ocr = state.get("is_scanned", False)
        
        # Directorio de salida: Carpeta con el nombre del PDF dentro del mismo directorio del PDF
        pdf_output_dir = os.path.join(pdf_dir, filename + "_export")
        os.makedirs(pdf_output_dir, exist_ok=True)
        
        print(f"📂 Exportando chunks a JSON (DEV) en: {pdf_output_dir}")
        
        # Agrupar chunks por página
        page_chunks = {}
        for i, chunk_data in enumerate(chunks):
            page_num = chunk_data["page"]
            if page_num not in page_chunks:
                page_chunks[page_num] = []
            
            # Metadata idéntica a la que se usará en Redis
            metadata = {
                "source": filename,
                "page_number": page_num,
                "chapter": chunk_data.get("chapter", "Sin Sección"),
                "sub_chapter": chunk_data.get("sub_chapter", ""),
                "total_pages": total_pages,
                "chunk_index": i,
                "is_ocr": is_ocr,
                "processed_at": datetime.datetime.now().isoformat(),
                "embedding_model": "text-embedding-3-small" # Referencial
            }
            
            page_chunks[page_num].append({
                "chunk": chunk_data["text"],
                "metadata": metadata
            })
            
        # Generar un JSON por página
        for page_num, items in page_chunks.items():
            json_filename = f"page_{page_num}.json"
            json_path = os.path.join(pdf_output_dir, json_filename)
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(items, f, ensure_ascii=False, indent=4)
                
        print(f"✅ {len(page_chunks)} archivos JSON generados.")
        return state
