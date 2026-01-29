import fitz

class ExtractStandardNode:
    @staticmethod
    def execute(state: dict) -> dict:
        """
        Orquestador del nodo.
        Maneja errores y garantiza que el grafo reciba un state consistente.
        """
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
        print(f"📄 Extrayendo texto (Standard): {pdf_path}")
        
        pages_content = []
        doc = fitz.open(pdf_path)
        for i, page in enumerate(doc):
            pages_content.append({
                "page": i + 1,
                "text": page.get_text()
            })
        doc.close()
        
        state["pages_content"] = pages_content
        state["total_pages"] = len(pages_content)
        state["status"] = "ok"
        return state


