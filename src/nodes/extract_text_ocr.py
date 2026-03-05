import base64
import fitz
from src.services.ai_engine.factory import AIProviderFactory

class ExtractTextOcrNode:
    @staticmethod
    def execute(state: dict) -> dict:
        try:
            return ExtractTextOcrNode._run(state)
        except Exception as e:
            state["status"] = "failed"
            state["error_node"] = "extract_text_ocr"
            state["error"] = str(e)
            print(f"❌ Error en ExtractTextOcrNode: {e}")
            return state

    @staticmethod
    def _run(state: dict) -> dict:
        pdf_path = state.get("current_pdf")
        print(f"🖼️ Extrayendo texto vía OCR (Factory): {pdf_path}")
        
        # Configuración específica para este nodo básico
        AI_CONFIG = {
            "engine": "openai",
            "model": "gpt-4o",
            "temperature": 0.0
        }
        
        proveedor = AIProviderFactory.get_provider(AI_CONFIG)
        doc = fitz.open(pdf_path)
        pages_content = []
        
        # Procesamos máximo 5 páginas para OCR (para no agotar créditos/tiempo en el demo)
        for i in range(min(5, len(doc))):
            page = doc[i]
            pix = page.get_pixmap()
            img_bytes = pix.tobytes("png")
            base64_image = base64.b64encode(img_bytes).decode('utf-8')
            
            system_prompt = "You are a simple OCR. Extract all text from this image."
            prompt = "Only provide the text found."
            
            # Extract elements but we only care about raw text for this node
            _, text, _, _ = proveedor.analyze_image(
                image_b64=base64_image,
                prompt=prompt,
                system_prompt=system_prompt,
                config=AI_CONFIG
            )
            
            pages_content.append({
                "page": i + 1,
                "text": text
            })
        
        doc.close()
        state["pages_content"] = pages_content
        state["total_pages"] = len(doc)
        state["status"] = "ok"
        return state
