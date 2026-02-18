import os
from typing import Literal
from langgraph.graph import StateGraph, END
from src.graph.batch_processor.node.load_pending import LoadPendingNode
from src.graph.batch_processor.node.process_document import ProcessDocumentNode

from src.graph.batch_processor.node.update_status import UpdateLicitacionStatusNode
from src.graph.batch_processor.node.trigger_semantic import TriggerSemanticNode
from src.constants.states import LicitacionStatus

def node_load_pending(state: dict) -> dict:
    return LoadPendingNode.execute(state)

def node_process_document(state: dict) -> dict:
    return ProcessDocumentNode.execute(state)

def node_update_status(state: dict) -> dict:
    return UpdateLicitacionStatusNode.execute(state)

def node_trigger_semantic(state: dict) -> dict:
    return TriggerSemanticNode.execute(state)

# Router para el bucle del lote
def router_batch_loop(state: dict) -> Literal["process", "end_batch"]:
    pdf_files = state.get("pdf_files", [])
    idx = state.get("current_index", 0)
    
    if idx < len(pdf_files):
        return "process"
    return "end_batch"

# Helper para setear estado objetivo antes de actualizar
def set_status_processing(state: dict) -> dict:
    state["target_licitacion_status"] = LicitacionStatus.PROCESANDO_DOCUMENTOS
    return state

def set_status_finished(state: dict) -> dict:
    # Determinar estado final basado en si hubo errores
    # Por ahora simplificado: Si terminó el loop, es DOCUMENTOS_PROCESADOS
    # Opcional: Checar si todos fallaron
    state["target_licitacion_status"] = LicitacionStatus.DOCUMENTOS_PROCESADOS
    return state

def build_batch_processor():
    workflow = StateGraph(dict)

    # Añadir nodos
    workflow.add_node("load_pending", node_load_pending)
    workflow.add_node("set_processing", set_status_processing)
    workflow.add_node("update_status_start", node_update_status)
    
    workflow.add_node("process_document", node_process_document)
    
    workflow.add_node("set_finished", set_status_finished)
    workflow.add_node("update_status_end", node_update_status)
    workflow.add_node("trigger_semantic", node_trigger_semantic)

    # Punto de entrada
    workflow.set_entry_point("load_pending")

    # Flujo: Load -> Set Processing -> Update DB -> Process Loop
    workflow.add_edge("load_pending", "set_processing")
    workflow.add_edge("set_processing", "update_status_start")
    workflow.add_edge("update_status_start", "process_document")
    
    # Bucle condicional
    workflow.add_conditional_edges(
        "process_document",
        router_batch_loop,
        {
            "process": "process_document",
            "end_batch": "set_finished"
        }
    )
    
    # Flujo Final: End Loop -> Set Finished -> Update DB -> Trigger Semantic -> End
    workflow.add_edge("set_finished", "update_status_end")
    workflow.add_edge("update_status_end", "trigger_semantic")
    workflow.add_edge("trigger_semantic", END)

    return workflow.compile()

if __name__ == "__main__":
    app = build_batch_processor()
    final_state = app.invoke({"current_index": 0})
    print("\n📊 Resumen de Procesamiento:")
    for file, status in final_state.get("file_states", {}).items():
        print(f"- {os.path.basename(file)}: {status}")
