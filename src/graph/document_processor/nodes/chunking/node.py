from .service import ChunkingService

class ChunkingNode:
    @staticmethod
    def execute(state: dict) -> dict:
        try:
            return ChunkingNode._run(state)
        except Exception as e:
            state["status"] = "failed"
            state["error_node"] = "chunking"
            state["error"] = str(e)
            print(f"❌ Error en ChunkingNode: {e}")
            return state

    @staticmethod
    def _run(state: dict) -> dict:
        extracted_elements = state.get("extracted_elements", [])
        pages_content = state.get("pages_content", [])
        
        chunks = []
        
        if extracted_elements:
            print("   -> Usando estrategia: Structured Elements (Vision)")
            chunks = ChunkingService.process_structured_elements(extracted_elements)
        elif pages_content:
             print("   -> Usando estrategia: Legacy Text Splitter")
             chunks = ChunkingService.chunk_text(pages_content)
        else:
             print("⚠️ ChunkingNode: No hay contenido para procesar")
             state["chunks"] = []
             return state
        
        state["chunks"] = chunks
        state["status"] = "ok"
        return state
