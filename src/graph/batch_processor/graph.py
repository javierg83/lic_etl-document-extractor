import os
from typing import Literal
from langgraph.graph import StateGraph, END
from src.graph.batch_processor.node.load_pending import LoadPendingNode
from src.graph.batch_processor.node.process_document import ProcessDocumentNode

def node_load_pending(state: dict) -> dict:
    return LoadPendingNode.execute(state)

def node_process_document(state: dict) -> dict:
    return ProcessDocumentNode.execute(state)

# Router para el bucle del lote
def router_batch_loop(state: dict) -> Literal["process", "end"]:
    pdf_files = state.get("pdf_files", [])
    idx = state.get("current_index", 0)
    
    if idx < len(pdf_files):
        return "process"
    return "end"

def build_batch_processor():
    workflow = StateGraph(dict)

    # Añadir nodos
    workflow.add_node("load_pending", node_load_pending)
    workflow.add_node("process_document", node_process_document)

    # Punto de entrada
    workflow.set_entry_point("load_pending")

    # Flujo inicial
    workflow.add_edge("load_pending", "process_document")
    
    # Bucle condicional
    workflow.add_conditional_edges(
        "process_document",
        router_batch_loop,
        {
            "process": "process_document",
            "end": END
        }
    )

    return workflow.compile()

if __name__ == "__main__":
    app = build_batch_processor()
    final_state = app.invoke({"current_index": 0})
    print("\n📊 Resumen de Procesamiento:")
    for file, status in final_state.get("file_states", {}).items():
        print(f"- {os.path.basename(file)}: {status}")
