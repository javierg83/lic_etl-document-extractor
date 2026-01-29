import os
from src.graph.document_processor import build_document_processor

# El subgrafo se compila una vez fuera para eficiencia si se desea, 
# o dentro si necesita ser dinámico. Aquí lo haremos una vez.
document_processor = build_document_processor()

class ProcessDocumentNode:
    @staticmethod
    def execute(state: dict) -> dict:
        """
        Llama al subgrafo para el archivo actual.
        """
        pdf_files = state.get("pdf_files", [])
        idx = state.get("current_index", 0)
        
        if idx >= len(pdf_files):
            return state

        current_file = pdf_files[idx]
        print(f"🚀 [Batch] Procesando: {os.path.basename(current_file)} ({idx+1}/{len(pdf_files)})")
        
        # Asegurar que file_states existe
        if "file_states" not in state:
            state["file_states"] = {}
            
        # Cambiar estado a 'procesando'
        state["file_states"][current_file] = "procesando"
        
        # Preparar input para el subgrafo
        sub_input = {
            "pdf_files": [current_file],
            "current_index": 0,
            "current_pdf": current_file
        }
        
        # Invocación sincrónica del subgrafo
        result = document_processor.invoke(sub_input)
        
        # Actualizar estado final del archivo baseado en el resultado del subgrafo
        if result.get("status") == "failed":
            print(f"❌ [Batch] Error procesando {os.path.basename(current_file)}")
            state["file_states"][current_file] = "error"
        else:
            print(f"✅ [Batch] Finalizado: {os.path.basename(current_file)}")
            state["file_states"][current_file] = "procesado"
        
        # Avanzar índice
        state["current_index"] = idx + 1
        return state
