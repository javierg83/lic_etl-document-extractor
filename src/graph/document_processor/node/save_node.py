from src.nodes.save_to_redis import SaveToRedisNode

class SaveNode:
    @staticmethod
    def execute(state: dict) -> dict:
        return SaveToRedisNode.execute(state)
