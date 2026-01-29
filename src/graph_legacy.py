from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END
from src.nodes.load_pdfs import LoadPdfsNode
from src.nodes.classify_pdf import ClassifyPdfNode
from src.nodes.extract_text_standard import ExtractTextStandardNode
from src.nodes.extract_text_ocr import ExtractTextOcrNode
from src.nodes.chunk_text import ChunkTextNode
from src.nodes.generate_embeddings import GenerateEmbeddingsNode
from src.nodes.save_to_redis import SaveToRedisNode
from src.nodes.export_json import ExportToJsonNode
from src.nodes.search_table_contents import SearchTableContentsNode
from src.nodes.simple_node import SimpleNode
from src.config import DEBUG_EXPORT_JSON

# En LangGraph, el state puede ser un dict directamente si se especifica en StateGraph(dict)
# Pero usaremos funciones envoltorio como solicitó el usuario.

def node_load_pdfs(state: dict) -> dict:
    print("➡️ Entrando al nodo: load_pdfs")
    return LoadPdfsNode.execute(state)

def node_classify_pdf(state: dict) -> dict:
    print("➡️ Entrando al nodo: classify_pdf")
    return ClassifyPdfNode.execute(state)

def node_extract_text_standard(state: dict) -> dict:
    print("➡️ Entrando al nodo: extract_text_standard")
    return ExtractTextStandardNode.execute(state)

def node_extract_text_ocr(state: dict) -> dict:
    print("➡️ Entrando al nodo: extract_text_ocr")
    return ExtractTextOcrNode.execute(state)

def node_chunk_text(state: dict) -> dict:
    print("➡️ Entrando al nodo: chunk_text")
    return ChunkTextNode.execute(state)

def node_generate_embeddings(state: dict) -> dict:
    print("➡️ Entrando al nodo: generate_embeddings")
    return GenerateEmbeddingsNode.execute(state)

def node_save_to_redis(state: dict) -> dict:
    print("➡️ Entrando al nodo: save_to_redis")
    return SaveToRedisNode.execute(state)

def node_export_json(state: dict) -> dict:
    print("➡️ Entrando al nodo: export_json")
    return ExportToJsonNode.execute(state)

def node_search_table_contents(state: dict) -> dict:
    print("➡️ Entrando al nodo: search_table_contents")
    return SearchTableContentsNode.execute(state)

def node_simple(state: dict) -> dict:
    print("➡️ Entrando al nodo: simple_node")
    return SimpleNode.execute(state)

# Router para decidir el tipo de extracción
def router_extraction(state: dict) -> Literal["extract_standard", "extract_ocr", "end"]:
    if state.get("status") == "failed":
        return "end"
    if state.get("all_processed"):
        return "end"
    
    return "extract_ocr" if state.get("is_scanned") else "extract_standard"

# Router para decidir si procesar el siguiente PDF
def router_loop(state: dict) -> Literal["classify", "end"]:
    pdf_files = state.get("pdf_files", [])
    idx = state.get("current_index", 0)
    
    if idx < len(pdf_files) and state.get("status") != "failed":
        return "classify"
    return "end"

def build_graph():
    # Iniciamos el grafo con dict como indica el usuario
    workflow = StateGraph(dict)

    # Añadir nodos
    workflow.add_node("load_pdfs", node_load_pdfs)
    workflow.add_node("classify_pdf", node_classify_pdf)
    workflow.add_node("extract_text_standard", node_extract_text_standard)
    workflow.add_node("extract_text_ocr", node_extract_text_ocr)
    workflow.add_node("search_table_contents", node_search_table_contents)    
    workflow.add_node("chunk_text", node_chunk_text)
    workflow.add_node("generate_embeddings", node_generate_embeddings)
    workflow.add_node("save_to_redis", node_save_to_redis)
    workflow.add_node("export_json", node_export_json)


    # Punto de entrada
    workflow.set_entry_point("load_pdfs")

    # Bordes y lógica de control
    workflow.add_edge("load_pdfs", "classify_pdf")

    # Decisión condicional después de clasificar
    workflow.add_conditional_edges(
        "classify_pdf",
        router_extraction,
        {
            "extract_standard": "extract_text_standard",
            "extract_ocr": "extract_text_ocr",
            "end": END
        }
    )

    # Ambas ramas de extracción van a la búsqueda de índice
    workflow.add_edge("extract_text_standard", "search_table_contents")
    workflow.add_edge("extract_text_ocr", "search_table_contents")

    # Del índice vamos al chunking
    workflow.add_edge("search_table_contents", "chunk_text")

    # Puente condicional para exportación a JSON (DEV) - Ahora antes de embeddings
    if DEBUG_EXPORT_JSON:
        workflow.add_edge("chunk_text", "export_json")
        workflow.add_edge("export_json", "generate_embeddings")
    else:
        workflow.add_edge("chunk_text", "generate_embeddings")

    workflow.add_edge("generate_embeddings", "save_to_redis")

    # Después de guardar, volvemos a clasificar el siguiente archivo o terminamos
    workflow.add_conditional_edges(
        "save_to_redis",
        router_loop,
        {
            "classify": "classify_pdf",
            "end": END
        }
    )

    return workflow.compile()

def build_simple_graph():
    workflow = StateGraph(dict)
    workflow.add_node("simple_node", node_simple)
    workflow.set_entry_point("simple_node")
    workflow.add_edge("simple_node", END)
    return workflow.compile()

if __name__ == "__main__":
    app = build_graph()
    # Para ejecutar:
    initial_state = {"pdf_files": [], "current_index": 0}
    app.invoke(initial_state)
    print("✅ Grafo construido y compilado con éxito.")
