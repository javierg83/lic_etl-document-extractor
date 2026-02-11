from .service import ExtractStandardService

class ExtractStandardNode:
    @staticmethod
    def execute(state: dict) -> dict:
        try:
            return ExtractStandardNode._run(state)
        except Exception as e:
            state["status"] = "failed"
            state["error_node"] = "extract_standard"
            state["error"] = str(e)
            print(f"❌ Error en ExtractStandardNode: {e}")
            return state

    @staticmethod
    def _run(state: dict) -> dict:
        pdf_path = state.get("current_pdf")
        if not pdf_path:
             print("⚠️ ExtractStandardNode: No hay PDF definido")
             return state

        # Llamamos al servicio
        pages_content = ExtractStandardService.extract_from_pdf(pdf_path)
        
        # Mantenemos consistencia en el output
        state["pages_content"] = pages_content
        state["status"] = "ok"
        return state
