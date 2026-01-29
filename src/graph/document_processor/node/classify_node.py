from src.nodes.classify_pdf import ClassifyPdfNode

class ClassifyNode:
    @staticmethod
    def execute(state: dict) -> dict:
        return ClassifyPdfNode.execute(state)
