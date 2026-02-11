from .service import SplitterService
import os

class SplitterNode:
    @staticmethod
    def execute(state: dict) -> dict:
        try:
            return SplitterNode._run(state)
        except Exception as e:
            state["status"] = "failed"
            state["error_node"] = "splitter"
            state["error"] = str(e)
            print(f"❌ Error en SplitterNode: {e}")
            return state

    @staticmethod
    def _run(state: dict) -> dict:
        # Obtenemos archivo y tipo desde el state (puesto allá por ClassifyNode)
        current_file = state.get("current_pdf")
        file_type = state.get("file_type")
        
        if not current_file:
             # Fallback logic legacy
             pdf_files = state.get("pdf_files", [])
             idx = state.get("current_index", 0)
             if idx < len(pdf_files):
                 current_file = pdf_files[idx]

        if not current_file:
            print("⚠️ SplitterNode: No hay archivo para procesar")
            return state

        # Asegurarnos de tener un file type para mostrar, o default
        display_type = file_type if file_type else "unknown"
        print(f"🔪 [Nodo Splitter]: Procesando {os.path.basename(current_file)} como {display_type}")
        
        result = SplitterService.identify_and_split(current_file, file_type)
        
        # El resto del state se llena según el resultado del split
        if result.get("type") == "pdf":
            state["is_scanned"] = result.get("is_scanned", False)
            state["total_pages"] = result.get("total_pages", 0)
            state["sub_documents"] = result.get("sub_documents", [])
            print(f"   📄 PDF procesado: {state['total_pages']} páginas.")
            
        elif result.get("type") == "excel":
            state["sub_documents"] = result.get("sub_documents", [])
            print(f"   📊 Excel detectado. Hojas encontradas: {len(state['sub_documents'])}")
            
        state["status"] = "ok"
        return state
