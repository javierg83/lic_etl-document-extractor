import os
from src.config import REPOSITORY
from src.utils.db import get_pending_files


class LoadPendingNode:
    @staticmethod
    def execute(state: dict) -> dict:
        """
        Orquestador del nodo.
        Maneja errores y garantiza que el grafo reciba un state consistente.
        """
        try:
            return LoadPendingNode._run(state)
        except Exception as e:
            state["status"] = "failed"
            state["error_node"] = "load_pending"
            state["error"] = str(e)
            print(f"❌ Error en LoadPendingNode: {e}")
            return state

    @staticmethod
    def _run(state: dict) -> dict:
        """
        Carga los archivos y marca el estado inicial.
        """
        licitacion_id = state.get("licitacion_id")
        
        if licitacion_id:
            print(f"📁 [Batch] Buscando archivos pendientes para Licitación {licitacion_id}...")
            print(f"🔍 [DEBUG] Intentando obtener archivos pendientes para licitacion_id: {licitacion_id}")
            files = get_pending_files(licitacion_id)
            print(f"✅ [DEBUG] Consulta exitosa, archivos encontrados: {len(files)}")
            
            pdf_files = [f["ruta_almacenamiento"] for f in files]
            # Mapeo de ruta a ID de base de datos para facilitar actualizaciones de estado
            file_ids = {f["ruta_almacenamiento"]: f["id"] for f in files}
            
            # NUEVO: Guardar IDs internos para usarlos en Redis
            # Asumimos que todos los archivos son de la misma licitación, por lo que el ID interno de licitación es el mismo
            if files:
                state["licitacion_internal_id"] = files[0]["licitacion_internal_id"]
                # Guardamos el UUID real de la licitación para usarlo en la cola semántica
                state["licitacion_uuid"] = files[0]["licitacion_uuid"]
            
            # Mapa de archivo -> id_interno_archivo
            state["file_internal_ids"] = {f["ruta_almacenamiento"]: f["archivo_internal_id"] for f in files}

            state["pdf_files"] = pdf_files
            state["file_ids"] = file_ids
            state["status"] = "ok" if pdf_files else "no_files"
            state["current_index"] = 0
            
            if not pdf_files:
                print(f"⚠️ No se encontraron archivos pendientes para la licitación {licitacion_id}")
        else:
            print("📁 [Batch] Buscando archivos locales...")
            repository = REPOSITORY
            print(f"📂 Revisando repositorio: {repository}")
            
            # Si ya vienen archivos en el state (desde el Worker), no escaneamos el REPOSITORY
            if not state.get("pdf_files"):
                if not os.path.exists(repository):
                    raise Exception(f"El directorio {repository} no existe.")
                    
                pdf_files = [os.path.join(repository, f) for f in os.listdir(repository) if f.lower().endswith('.pdf')]
                
                if not pdf_files:
                    print("⚠️ No se encontraron archivos PDF.")
                    state["pdf_files"] = []
                    state["status"] = "no_files"
                else:
                    state["pdf_files"] = pdf_files
                    state["status"] = "ok"
                    print(f"✅ Se encontraron {len(pdf_files)} archivos PDF.")
            else:
                print(f"✅ Usando archivos proporcionados: {state['pdf_files']}")
                state["status"] = "ok"
            
            state["current_index"] = 0

        
        if state.get("status") == "ok":
            # Inicializar estados de archivos si no existen
            pdf_files = state.get("pdf_files", [])
            if "file_states" not in state:
                state["file_states"] = {f: "PENDIENTE" for f in pdf_files}
        
        return state

