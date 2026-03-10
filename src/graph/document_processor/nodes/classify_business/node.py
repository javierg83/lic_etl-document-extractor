import json
from src.services.ai_engine.factory import AIProviderFactory

class ClassifyBusinessNode:
    """
    Nodo encargado de clasificar el tipo de negocio o documento (ej: 'LICITACION_PUBLICA', 'COMPRA_AGIL').
    Esto es crucial para que el OCR visual sepa luego si deducir formato de tabla estricta o texto libre.
    """
    @staticmethod
    def execute(state: dict) -> dict:
        print("[NODE] Ejecutando ClassifyBusinessNode...")
        
        file_name = state.get("filename_clean", state.get("pdf_files", [""])[0] if state.get("pdf_files") else "")
        
        prompt = f"""
        Analiza el nombre del siguiente documento asociado a procesos de adquisiciones gubernamentales/públicas.
        
        Nombre del archivo: {file_name}
        
        Tu tarea es determinar si este documento corresponde a una Licitacion Pública tradicional, o a una "Compra Ágil" (como una cotización directa o un requerimiento rápido de menor formato).
        
        Devuelve tu respuesta ÚNICAMENTE como un JSON válido con la clave "tipo_adquisicion" y el valor "LICITACION_PUBLICA" o "COMPRA_AGIL".
        Si no estás seguro, asume "LICITACION_PUBLICA".
        """
        
        try:
            config = {
                "engine": "gemini",  
                "model": "gemini-2.5-flash", 
                "temperature": 0.0
            }
            proveedor = AIProviderFactory.get_provider(config)
            
            response_text, usage = proveedor.generate_text(
                prompt=prompt,
                system_prompt="Devuelve un JSON válido.",
                config=config
            )
            
            # Limpiar posible markdown en la respuesta
            clean_text = response_text.replace("```json", "").replace("```", "").strip()
            data = json.loads(clean_text)
            
            tipo = data.get("tipo_adquisicion", "LICITACION_PUBLICA")
            state["tipo_adquisicion"] = tipo
            print(f"[ClassifyBusinessNode] Documento clasificado estructuralmente como: {tipo}")
            
        except Exception as e:
            print(f"[ClassifyBusinessNode] Error al clasificar (fallback a LICITACION_PUBLICA): {e}")
            state["tipo_adquisicion"] = "LICITACION_PUBLICA"
            
        return state
