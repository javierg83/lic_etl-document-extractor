from src.nodes.extract_text_ocr import ExtractTextOcrNode

class ExtractOcrNode:
    @staticmethod
    def execute(state: dict) -> dict:
        return ExtractTextOcrNode.execute(state)
