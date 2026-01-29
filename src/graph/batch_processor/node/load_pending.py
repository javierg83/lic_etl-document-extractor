from src.nodes.load_pdfs import LoadPdfsNode
from src.utils.db import get_pending_files

class LoadPendingNode:
    @staticmethod
    def execute(state: dict) -> dict:
        """
        Carga los archivos y marca el estado inicial.
        """
        licitacion_id = state.get("licitacion_id")
        
        if licitacion_id:
            print(f"📁 [Batch] Buscando archivos pendientes para Licitación {licitacion_id}...")
            files = get_pending_files(licitacion_id)
            
            pdf_files = [f["ruta_almacenamiento"] for f in files]
            # Mapeo de ruta a ID de base de datos para facilitar actualizaciones de estado
            file_ids = {f["ruta_almacenamiento"]: f["id"] for f in files}
            
            state["pdf_files"] = pdf_files
            state["file_ids"] = file_ids
            state["status"] = "ok" if pdf_files else "no_files"
            state["current_index"] = 0
            
            if not pdf_files:
                print(f"⚠️ No se encontraron archivos pendientes para la licitación {licitacion_id}")
        else:
            print("📁 [Batch] Buscando archivos locales...")
            state = LoadPdfsNode.execute(state)
        
        if state.get("status") == "ok":
            # Inicializar estados de archivos si no existen
            pdf_files = state.get("pdf_files", [])
            if "file_states" not in state:
                state["file_states"] = {f: "PENDIENTE" for f in pdf_files}
        
        return state
