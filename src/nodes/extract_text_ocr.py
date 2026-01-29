import base64
import fitz
from openai import OpenAI
from src.config import OPENAI_API_KEY

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
        print(f"🖼️ Extrayendo texto vía OCR (OpenAI): {pdf_path}")
        
        client = OpenAI(api_key=OPENAI_API_KEY)
        doc = fitz.open(pdf_path)
        pages_content = []
        
        # Procesamos máximo 5 páginas para OCR (para no agotar créditos/tiempo en el demo)
        for i in range(min(5, len(doc))):
            page = doc[i]
            pix = page.get_pixmap()
            img_bytes = pix.tobytes("png")
            base64_image = base64.b64encode(img_bytes).decode('utf-8')
            
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Extract all text from this image. Only provide the text found."},
                            {
                                 "type": "image_url",
                                 "image_url": {"url": f"data:image/png;base64,{base64_image}"},
                            },
                        ],
                    }
                ],
            )
            text = response.choices[0].message.content
            pages_content.append({
                "page": i + 1,
                "text": text
            })
        
        doc.close()
        state["pages_content"] = pages_content
        state["total_pages"] = len(doc)
        state["status"] = "ok"
        return state
