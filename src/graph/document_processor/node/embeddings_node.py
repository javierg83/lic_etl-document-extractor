from src.nodes.generate_embeddings import GenerateEmbeddingsNode

class EmbeddingsNode:
    @staticmethod
    def execute(state: dict) -> dict:
        return GenerateEmbeddingsNode.execute(state)
