import os
from src.graph.document_processor import build_document_processor
from src.utils.db import change_status

# El subgrafo se compila una vez fuera para eficiencia si se desea, 
# o dentro si necesita ser dinámico. Aquí lo haremos una vez.
document_processor = build_document_processor()

class ProcessDocumentNode:
    @staticmethod
    def execute(state: dict) -> dict:
        """
        Llama al subgrafo para el archivo actual e informa el estado a la DB.
        """
        pdf_files = state.get("pdf_files", [])
        idx = state.get("current_index", 0)
        file_ids = state.get("file_ids", {})
        
        if idx >= len(pdf_files):
            return state

        current_file = pdf_files[idx]
        current_file_id = file_ids.get(current_file)
        
        print(f"🚀 [Batch] Procesando: {os.path.basename(current_file)} ({idx+1}/{len(pdf_files)})")
        
        # Asegurar que file_states existe
        if "file_states" not in state:
            state["file_states"] = {}
            
        # Cambiar estado a 'PROCESANDO'
        state["file_states"][current_file] = "PROCESANDO"
        
        # Actualización en Base de Datos
        if current_file_id:
            change_status(current_file_id, "PROCESANDO")
            # --- LÍNEA PARA VISUALIZACIÓN TEMPORAL ---
            input(f"⏳ Estado cambiado a 'PROCESANDO' para {os.path.basename(current_file)}. Presione Enter para continuar...")
            # ---------------------------------------
        
        # Preparar input para el subgrafo
        sub_input = {
            "pdf_files": [current_file],
            "current_index": 0,
            "current_pdf": current_file
        }
        
        # Invocación sincrónica del subgrafo
        result = document_processor.invoke(sub_input)
        
        # Actualizar estado final del archivo baseado en el resultado del subgrafo
        final_status = "PROCESADO"
        if result.get("status") == "failed":
            print(f"❌ [Batch] Error procesando {os.path.basename(current_file)}")
            final_status = "ERROR"
        else:
            print(f"✅ [Batch] Finalizado: {os.path.basename(current_file)}")
            final_status = "PROCESADO"
            
        state["file_states"][current_file] = final_status
        
        # Actualización final en Base de Datos
        if current_file_id:
            change_status(current_file_id, final_status)
        
        # Avanzar índice
        state["current_index"] = idx + 1
        return state
