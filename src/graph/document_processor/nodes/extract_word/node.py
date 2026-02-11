from .service import ExtractWordService

class ExtractWordNode:
    @staticmethod
    def execute(state: dict) -> dict:
        try:
            return ExtractWordNode._run(state)
        except Exception as e:
            state["status"] = "failed"
            state["error_node"] = "extract_word"
            state["error"] = str(e)
            print(f"❌ Error en ExtractWordNode: {e}")
            return state

    @staticmethod
    def _run(state: dict) -> dict:
        file_path = state.get("current_pdf")
        
        pages_content = ExtractWordService.extract_text(file_path)
        
        state["pages_content"] = pages_content
        state["status"] = "ok"
        return state
