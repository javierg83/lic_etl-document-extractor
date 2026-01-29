class SimpleNode:
    @staticmethod
    def execute(state: dict) -> dict:
        """
        Orquestador del nodo.
        Maneja errores y garantiza que el grafo reciba un state consistente.
        """
        try:
            return SimpleNode._run(state)
        except Exception as e:
            state["status"] = "failed"
            state["error_node"] = "simple"
            state["error"] = str(e)
            print(f"❌ Error en SimpleNode: {e}")
            return state

    @staticmethod
    def _run(state: dict) -> dict:
        pdf_files = state.get("pdf_files", [])
        current_index = state.get("current_index", 0)
        
        if current_index < len(pdf_files):
            file_path = pdf_files[current_index]
            print(f"📖 Leyendo archivo: {file_path}")
            # En un caso real aquí se leería el archivo
        
        state["current_index"] = current_index + 1
        state["status"] = "ok"
        return state
