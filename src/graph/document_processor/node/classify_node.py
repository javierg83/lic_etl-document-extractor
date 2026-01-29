import fitz  # PyMuPDF
import os

class ClassifyNode:
    @staticmethod
    def execute(state: dict) -> dict:
        """
        Orquestador del nodo.
        Maneja errores y garantiza que el grafo reciba un state consistente.
        """
        try:
            return ClassifyNode._run(state)
        except Exception as e:
            state["status"] = "failed"
            state["error_node"] = "classify"
            state["error"] = str(e)
            print(f"❌ Error en ClassifyNode: {e}")
            return state

    @staticmethod
    def _run(state: dict) -> dict:
        pdf_files = state.get("pdf_files", [])
        idx = state.get("current_index", 0)
        
        if idx >= len(pdf_files):
            state["all_processed"] = True
            return state
            
        pdf_path = pdf_files[idx]
        print(f"🔍 Clasificando: {os.path.basename(pdf_path)}")
        
        doc = fitz.open(pdf_path)
        is_scanned = True
        
        # Revisamos las primeras 3 páginas para ver si hay texto extraíble
        for i in range(min(3, len(doc))):
            text = doc[i].get_text().strip()
            if len(text) > 50:  # Umbral arbitrario para considerar que hay texto
                is_scanned = False
                break
        doc.close()
        
        state["is_scanned"] = is_scanned
        state["pdf_type"] = "image" if is_scanned else "text"
        state["current_pdf"] = pdf_path
        state["status"] = "ok"
        
        print(f"📊 Tipo detectado: {'Imagen/Escaneado' if is_scanned else 'Texto Normal'}")
        
        return state


