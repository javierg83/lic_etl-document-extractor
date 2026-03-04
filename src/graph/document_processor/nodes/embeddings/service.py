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
        
        # Preparamos textos para la API, evitando el límite de 8192 tokens
        import tiktoken
        encoding = tiktoken.get_encoding("cl100k_base")
        
        texts = []
        for chunk in chunks:
            text = chunk["text"].replace("\n", " ")
            tokens = encoding.encode(text, disallowed_special=())
            if len(tokens) > 8000:
                print(f"   ⚠️ Limitando chunk de {len(tokens)} tokens a 8000 para evitar error 400.")
                text = encoding.decode(tokens[:8000])
            texts.append(text)
        
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
