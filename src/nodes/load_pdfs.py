import os
from src.config import REPOSITORY

class LoadPdfsNode:
    @staticmethod
    def execute(state: dict) -> dict:
        """
        Orquestador del nodo.
        Maneja errores y garantiza que el grafo reciba un state consistente.
        """
        try:
            return LoadPdfsNode._run(state)
        except Exception as e:
            state["status"] = "failed"
            state["error_node"] = "load_pdfs"
            state["error"] = str(e)
            print(f"❌ Error en LoadPdfsNode: {e}")
            return state

    @staticmethod
    def _run(state: dict) -> dict:
        repository = REPOSITORY
        print(f"📂 Revisando repositorio: {repository}")
        
        # Si ya vienen archivos en el state (desde el Worker), no escaneamos el REPOSITORY
        if state.get("pdf_files"):
            print(f"✅ Usando archivos proporcionados: {state['pdf_files']}")
            state["status"] = "ok"
            state["current_index"] = 0
            return state

        if not os.path.exists(repository):
            raise Exception(f"El directorio {repository} no existe.")
            
        pdf_files = [os.path.join(repository, f) for f in os.listdir(repository) if f.lower().endswith('.pdf')]
        
        if not pdf_files:
            print("⚠️ No se encontraron archivos PDF.")
            state["pdf_files"] = []
            state["status"] = "no_files"
            return state

        state["pdf_files"] = pdf_files
        state["current_index"] = 0
        state["status"] = "ok"
        print(f"✅ Se encontraron {len(pdf_files)} archivos PDF.")
        
        return state
