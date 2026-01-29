from src.graph import build_graph

def main():
    print("🚀 Iniciando procesamiento de PDFs...")
    
    # Compilar el grafo
    app = build_graph()
    
    # Estado inicial
    # Nota: El nodo load_pdfs se encarga de buscar los archivos en el REPOSITORY definido en config
    initial_state = {
        "pdf_files": [], 
        "current_index": 0,
        "status": "init"
    }
    
    # Ejecutar el grafo
    result = app.invoke(initial_state)
    
    if result.get("status") == "failed":
        print(f"❌ El proceso terminó con errores: {result.get('error')}")
    else:
        print("🎉 Procesamiento completado exitosamente.")

if __name__ == "__main__":
    main()
