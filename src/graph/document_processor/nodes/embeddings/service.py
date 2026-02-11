from openai import OpenAI
from src.config import OPENAI_API_KEY

class EmbeddingsService:
    @staticmethod
    def generate_embeddings(chunks: list) -> list:
        """
        Genera embeddings para una lista de chunks.
        """
        print(f"🧠 [Nodo Embeddings]: Generando Embeddings para {len(chunks)} chunks...")
        
        if not chunks:
            return []
            
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        # Preparamos textos para la API
        texts = [chunk["text"].replace("\n", " ") for chunk in chunks]
        
        try:
            response = client.embeddings.create(
                input=texts,
                model="text-embedding-3-small"
            )
            
            # Asignamos embeddings de vuelta a los chunks
            for i, data in enumerate(response.data):
                chunks[i]["embedding"] = data.embedding
                
            print(f"   🧠 Embeddings generados exitosamente: {len(response.data)}")
            return chunks
            
        except Exception as e:
            print(f"❌ Error OpenAI Embeddings: {e}")
            raise e
