from openai import OpenAI
from src.config import OPENAI_API_KEY

class EmbeddingsNode:
    @staticmethod
    def execute(state: dict) -> dict:
        """
        Orquestador del nodo.
        Maneja errores y garantiza que el grafo reciba un state consistente.
        """
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
            print("⚠️ No hay fragmentos para embeber.")
            state["status"] = "no_chunks"
            return state
            
        print(f"🧠 Generando embeddings para {len(chunks)} fragmentos...")
        
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        # Extraemos solo el texto para la API de embeddings
        texts = [c["text"] for c in chunks]
        
        # Obtenemos los embeddings en bloque
        response = client.embeddings.create(
            input=texts,
            model="text-embedding-3-small"
        )
        
        embeddings = [data.embedding for data in response.data]
        
        state["embeddings"] = embeddings
        state["status"] = "ok"
        print(f"✅ Embeddings generados exitosamente.")
        
        return state


