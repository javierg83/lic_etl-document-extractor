from .service import ExtractExcelService

class ExtractExcelNode:
    @staticmethod
    def execute(state: dict) -> dict:
        try:
            return ExtractExcelNode._run(state)
        except Exception as e:
            state["status"] = "failed"
            state["error_node"] = "extract_excel"
            state["error"] = str(e)
            print(f"❌ Error en ExtractExcelNode: {e}")
            return state

    @staticmethod
    def _run(state: dict) -> dict:
        file_path = state.get("current_pdf") # Usamos el mismo key por compatibilidad, o podríamos usar 'current_file'
        
        pages_content = ExtractExcelService.extract_text(file_path)
        
        state["pages_content"] = pages_content
        state["status"] = "ok"
        return state
