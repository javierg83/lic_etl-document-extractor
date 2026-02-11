from .utils import detect_file_type
import os

class ClassifyNode:
    @staticmethod
    def execute(state: dict) -> dict:
        try:
            return ClassifyNode._run(state)
        except Exception as e:
            state["status"] = "failed"
            state["error_node"] = "classify"
            state["error"] = str(e)
            print(f"❌ Error en ClassifyNode: {e}")
            return state

    @staticmethod
    def _run(state: dict) -> dict:
        # Lógica para obtener el archivo actual (igual que antes)
        pdf_files = state.get("pdf_files", [])
        idx = state.get("current_index", 0)
        
        current_file = None
        if "current_pdf" in state:
             current_file = state["current_pdf"]
        elif idx < len(pdf_files):
             current_file = pdf_files[idx]
             
        if not current_file:
            print("⚠️ ClassifyNode: No hay archivo para procesar")
            return state

        print(f"🔍 [Nodo Classify]: Analizando tipo de {os.path.basename(current_file)}")
        
        # 1. Detectar Tipo
        file_type = detect_file_type(current_file)
        state["file_type"] = file_type
        state["current_pdf"] = current_file # Aseguramos que el path esté explícito
        
        print(f"   📂 Tipo detectado: {file_type}")
        
        state["status"] = "ok"
        return state
