from .service import SaveService
import os

class SaveNode:
    @staticmethod
    def execute(state: dict) -> dict:
        try:
            return SaveNode._run(state)
        except Exception as e:
            state["status"] = "failed"
            state["error_node"] = "save"
            state["error"] = str(e)
            print(f"❌ Error en SaveNode: {e}")
            return state

    @staticmethod
    def _run(state: dict) -> dict:
        chunks = state.get("chunks", [])
        licitacion_id = state.get("licitacion_id") # Debe venir desde el Batch Processor
        current_pdf = state.get("current_pdf")
        
        if not chunks:
             print("⚠️ SaveNode: No hay chunks para guardar")
             return state
             
        # Fallback si licitacion_id no está (ej: pruebas unitarias)
        # Fallback si licitacion_id no está (ej: pruebas unitarias)
        if not licitacion_id:
            print("⚠️ SaveNode: licitacion_id no encontrado en state. Usando 'default'")
            licitacion_id = "default"

        filename_clean = state.get("filename_clean")
        if not filename_clean:
             # Fallback si no viene limpio
             filename_clean = os.path.splitext(os.path.basename(current_pdf))[0]

        # Obtener IDs internos para la llave de Redis
        licitacion_internal_id = state.get("licitacion_internal_id")
        file_internal_ids = state.get("file_internal_ids", {})
        archivo_internal_id = file_internal_ids.get(current_pdf)

        if not licitacion_internal_id or not archivo_internal_id:
            print(f"⚠️ SaveNode: Faltan IDs internos para {filename_clean}. Usando comportamiento legacy (UUIDs/Nombre).")
            # Podríamos optar por fallar, o dejar que el servicio maneje nulos si queremos compatibilidad.
            # Por ahora pasamos None y que el servicio decida o use fallback.
        
        SaveService.save_to_redis(
            licitacion_id=licitacion_id, 
            filename_clean=filename_clean, 
            file_path=current_pdf, 
            chunks=chunks,
            licitacion_internal_id=licitacion_internal_id,
            archivo_internal_id=archivo_internal_id
        )
        
        state["status"] = "ok"
        return state
