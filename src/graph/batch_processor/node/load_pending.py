from src.nodes.load_pdfs import LoadPdfsNode

class LoadPendingNode:
    @staticmethod
    def execute(state: dict) -> dict:
        """
        Carga los archivos y marca el estado inicial.
        """
        print("📁 [Batch] Buscando archivos pendientes...")
        state = LoadPdfsNode.execute(state)
        
        if state.get("status") == "ok":
            # Inicializar estados de archivos si no existen
            pdf_files = state.get("pdf_files", [])
            # Evitar sobrescribir si ya existe (por ejemplo en reintentos o worker)
            if "file_states" not in state:
                state["file_states"] = {f: "pendiente" for f in pdf_files}
        
        return state
