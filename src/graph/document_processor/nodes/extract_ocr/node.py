from .service import ExtractOcrService

class ExtractOcrNode:
    @staticmethod
    def execute(state: dict) -> dict:
        try:
            return ExtractOcrNode._run(state)
        except Exception as e:
            state["status"] = "failed"
            state["error_node"] = "extract_text_ocr"
            state["error"] = str(e)
            print(f"❌ Error en ExtractOcrNode: {e}")
            return state

    @staticmethod
    def _run(state: dict) -> dict:
        # Recuperamos el archivo a procesar
        # Nota: En el futuro, idealmente esto recibiría una "TASK" de página individual
        # Por ahora mantenemos compatibilidad procesando el PDF "current_pdf"
        
        pdf_path = state.get("current_pdf")
        if not pdf_path:
             print("⚠️ ExtractOcrNode: No hay PDF definido en state['current_pdf']")
             return state

        # Llamamos al servicio
        pages_content = ExtractOcrService.extract_from_pdf(pdf_path)
        
        # Actualizamos state
        # Actualizamos state
        # IMPORTANTE: Ahora guardamos elementos estructurados
        state["extracted_elements"] = pages_content # extract_from_pdf returns elements list now
        state["pages_content"] = [] # Clear or leave empty to avoid confusion in ChunkingNode
        
        # Opcional: Actualizar el estado de "sub_documents" si quisiéramos ser consistentes con el Splitter
        # Pero por compatibilidad con los nodos siguientes (chunking), mantenemos 'pages_content'
        
        state["status"] = "ok"
        return state
