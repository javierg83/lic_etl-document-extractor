from .service import EmbeddingsService

class EmbeddingsNode:
    @staticmethod
    def execute(state: dict) -> dict:
        try:
            return EmbeddingsNode._run(state)
        except Exception as e:
            state["status"] = "failed"
            state["error_node"] = "embeddings"
            state["error"] = str(e)
            print(f"❌ Error en EmbeddingsNode: {e}")
            return state

    @staticmethod
    def _run(state: dict) -> dict:
        chunks = state.get("chunks", [])
        
        if not chunks:
             print("⚠️ EmbeddingsNode: No hay chunks para procesar")
             return state

        # Modifica la lista in-place agregando el vector
        chunks_with_embeddings = EmbeddingsService.generate_embeddings(chunks)
        
        state["chunks"] = chunks_with_embeddings
        state["status"] = "ok"
        return state
