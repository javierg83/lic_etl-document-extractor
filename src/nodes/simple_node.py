class SimpleNode:
    @staticmethod
    def execute(state: dict) -> dict:
        pdf_files = state.get("pdf_files", [])
        current_index = state.get("current_index", 0)
        
        if current_index < len(pdf_files):
            file_path = pdf_files[current_index]
            print(f"📖 Leyendo archivo: {file_path}")
            # En un caso real aquí se leería el archivo
        
        state["current_index"] = current_index + 1
        state["status"] = "ok"
        return state
