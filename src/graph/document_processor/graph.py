from typing import Literal
from langgraph.graph import StateGraph, END

# Importación de nodos locales del paquete
from src.graph.document_processor.node.classify_node import ClassifyNode
from src.graph.document_processor.node.extract_standard_node import ExtractStandardNode
from src.graph.document_processor.node.extract_ocr_node import ExtractOcrNode
from src.graph.document_processor.node.chunking_node import ChunkingNode
from src.graph.document_processor.node.embeddings_node import EmbeddingsNode
from src.graph.document_processor.node.save_node import SaveNode

# Envoltorios (estilo execute solicitado)
def node_classify_pdf(state: dict) -> dict:
    return ClassifyNode.execute(state)

def node_extract_text_standard(state: dict) -> dict:
    return ExtractStandardNode.execute(state)

def node_extract_text_ocr(state: dict) -> dict:
    return ExtractOcrNode.execute(state)

def node_chunk_text(state: dict) -> dict:
    return ChunkingNode.execute(state)

def node_generate_embeddings(state: dict) -> dict:
    return EmbeddingsNode.execute(state)

def node_save_to_redis(state: dict) -> dict:
    return SaveNode.execute(state)

# Router
def router_extraction(state: dict) -> Literal["extract_standard", "extract_ocr", "end"]:
    if state.get("status") == "failed":
        return "end"
    return "extract_ocr" if state.get("is_scanned") else "extract_standard"

def build_document_processor():
    workflow = StateGraph(dict)

    workflow.add_node("classify", node_classify_pdf)
    workflow.add_node("extract_standard", node_extract_text_standard)
    workflow.add_node("extract_ocr", node_extract_text_ocr)
    workflow.add_node("chunking", node_chunk_text)
    workflow.add_node("embeddings", node_generate_embeddings)
    workflow.add_node("save", node_save_to_redis)

    workflow.set_entry_point("classify")

    workflow.add_conditional_edges(
        "classify",
        router_extraction,
        {
            "extract_standard": "extract_standard",
            "extract_ocr": "extract_ocr",
            "end": END
        }
    )

    workflow.add_edge("extract_standard", "chunking")
    workflow.add_edge("extract_ocr", "chunking")
    workflow.add_edge("chunking", "embeddings")
    workflow.add_edge("embeddings", "save")
    workflow.add_edge("save", END)

    return workflow.compile()
