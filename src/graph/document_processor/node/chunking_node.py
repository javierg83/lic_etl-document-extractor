from src.nodes.chunk_text import ChunkTextNode

class ChunkingNode:
    @staticmethod
    def execute(state: dict) -> dict:
        return ChunkTextNode.execute(state)
