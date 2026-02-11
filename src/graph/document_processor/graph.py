from typing import Literal
from langgraph.graph import StateGraph, END

# Importación de nuevos nodos refactorizados
from src.graph.document_processor.nodes.classify.node import ClassifyNode
from src.graph.document_processor.nodes.splitter.node import SplitterNode
from src.graph.document_processor.nodes.extract_standard.node import ExtractStandardNode
from src.graph.document_processor.nodes.extract_ocr.node import ExtractOcrNode
from src.graph.document_processor.nodes.extract_excel.node import ExtractExcelNode
from src.graph.document_processor.nodes.extract_word.node import ExtractWordNode
from src.graph.document_processor.nodes.chunking.node import ChunkingNode
from src.graph.document_processor.nodes.embeddings.node import EmbeddingsNode
from src.graph.document_processor.nodes.save.node import SaveNode

# Envoltorios de ejecución
def node_classify(state: dict) -> dict: return ClassifyNode.execute(state)
def node_splitter(state: dict) -> dict: return SplitterNode.execute(state)
def node_extract_standard(state: dict) -> dict: return ExtractStandardNode.execute(state)
def node_extract_ocr(state: dict) -> dict: return ExtractOcrNode.execute(state)
def node_extract_excel(state: dict) -> dict: return ExtractExcelNode.execute(state)
def node_extract_word(state: dict) -> dict: return ExtractWordNode.execute(state)
def node_chunking(state: dict) -> dict: return ChunkingNode.execute(state)
def node_embeddings(state: dict) -> dict: return EmbeddingsNode.execute(state)
def node_save(state: dict) -> dict: return SaveNode.execute(state)

# Router Inteligente
def router_extraction(state: dict) -> Literal["extract_standard", "extract_ocr", "extract_excel", "extract_word", "end"]:
    if state.get("status") == "failed":
        return "end"
        
    file_type = state.get("file_type", "unknown")
    is_scanned = state.get("is_scanned", False)
    
    if file_type == "pdf":
        return "extract_ocr" if is_scanned else "extract_standard"
    elif file_type == "excel":
        return "extract_excel"
    elif file_type == "word":
        return "extract_word"
    else:
        print(f"⚠️ Tipo de archivo desconocido o no soportado para extracción: {file_type}")
        return "end"

def build_document_processor():
    workflow = StateGraph(dict)

    # Nodos
    workflow.add_node("classify", node_classify)
    workflow.add_node("splitter", node_splitter) # Aunque por ahora es passthrough en la cadena lineal
    
    workflow.add_node("extract_standard", node_extract_standard)
    workflow.add_node("extract_ocr", node_extract_ocr)
    workflow.add_node("extract_excel", node_extract_excel)
    workflow.add_node("extract_word", node_extract_word)
    
    workflow.add_node("chunking", node_chunking)
    workflow.add_node("embeddings", node_embeddings)
    workflow.add_node("save", node_save)

    # Definición del Flujo
    workflow.set_entry_point("classify")
    
    # Classify -> Splitter
    workflow.add_edge("classify", "splitter")

    # Splitter -> Router -> Extractores
    # Nota: El Router usa el state enriquecido por Classify y Splitter
    workflow.add_conditional_edges(
        "splitter",
        router_extraction,
        {
            "extract_standard": "extract_standard",
            "extract_ocr": "extract_ocr",
            "extract_excel": "extract_excel",
            "extract_word": "extract_word",
            "end": END
        }
    )

    # Convergencia: Todos los extractores van a Chunking
    workflow.add_edge("extract_standard", "chunking")
    workflow.add_edge("extract_ocr", "chunking")
    workflow.add_edge("extract_excel", "chunking")
    workflow.add_edge("extract_word", "chunking")
    
    # Pipeline Lineal Final
    workflow.add_edge("chunking", "embeddings")
    workflow.add_edge("embeddings", "save")
    workflow.add_edge("save", END)

    return workflow.compile()
