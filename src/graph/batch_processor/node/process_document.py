import os
from src.graph.document_processor.graph import build_document_processor

from src.utils.db import change_status

# El subgrafo se compila una vez fuera para eficiencia si se desea, 
# o dentro si necesita ser dinámico. Aquí lo haremos una vez.
document_processor = build_document_processor()

class ProcessDocumentNode:
    @staticmethod
    def execute(state: dict) -> dict:
        """
        Orquestador del nodo.
        Maneja errores y garantiza que el grafo reciba un state consistente.
        """
        try:
            return ProcessDocumentNode._run(state)
        except Exception as e:
            state["status"] = "failed"
            state["error_node"] = "process_document"
            state["error"] = str(e)
            print(f"❌ Error en ProcessDocumentNode: {e}")
            return state

    @staticmethod
    def _run(state: dict) -> dict:
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
        filename_clean = os.path.basename(current_file)
        
        # Strip licitacion_id prefix if present (format: {uuid}_{filename})
        lic_id = state.get("licitacion_id")
        if lic_id and filename_clean.startswith(f"{lic_id}_"):
            filename_clean = filename_clean[len(lic_id)+1:]
        
        sub_input = {
            "pdf_files": [current_file],
            "current_index": 0,
            "current_pdf": current_file,
            "licitacion_id": state.get("licitacion_id"),
            "filename_clean": filename_clean,
            # Pass internal IDs for Redis keys
            "licitacion_internal_id": state.get("licitacion_internal_id"),
            "file_internal_ids": state.get("file_internal_ids"),
            "archivo_internal_id": file_ids.get(current_file) # Assuming file_ids might map to internal ID or use the dict
        }
        
        # Correction: file_ids in LoadPendingNode maps path -> UUID (id). 
        # state["file_internal_ids"] maps path -> int (id_interno).
        # We need the int one.
        file_internal_ids = state.get("file_internal_ids", {})
        sub_input["archivo_internal_id"] = file_internal_ids.get(current_file)
        
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
            
            # --- NUEVO: Acumular ID para trigger semántico ---
            # Necesitamos el ID interno formato Redis: <lic_int>_<file_int>_<filename_clean>
            # Ya lo calculamos en el subgrafo (SaveService), pero aquí lo reconstruimos o lo pasamos.
            # Lo más seguro es reconstruirlo igual que SaveService.
            lic_int = state.get("licitacion_internal_id")
            file_int = file_ids.get(current_file) # Esto es UUID en state original... wait.
            # Corrección: file_ids en LoadPendingNode es ruta->UUID. 
            # file_internal_ids es ruta->int. Usemos ese.
            file_int = file_internal_ids.get(current_file)
            
            if lic_int and file_int:
                redis_doc_id = f"{lic_int}_{file_int}_{filename_clean}"
                if "processed_files" not in state:
                    state["processed_files"] = []
                state["processed_files"].append(redis_doc_id)
                print(f"📦 [Batch] Archivo agregado a lista de procesados: {redis_doc_id}")
            else:
                print(f"⚠️ [Batch] No se pudo generar ID Redis para {os.path.basename(current_file)} (Faltan IDs internos)")

        state["file_states"][current_file] = final_status
        
        # Actualización final en Base de Datos
        if current_file_id:
            change_status(current_file_id, final_status)
        
        # Avanzar índice
        state["current_index"] = idx + 1
        return state

