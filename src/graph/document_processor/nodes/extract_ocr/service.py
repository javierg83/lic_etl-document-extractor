import base64
import json
import fitz
from src.services.ai_engine.factory import AIProviderFactory
from .prompts import EXTRACT_TEXT_PROMPT, AI_CONFIG
from src.utils.image_filters import enhance_image_contrast
from src.utils.pdf_utils import extract_page_image

class ExtractOcrService:
    @staticmethod
    def extract_from_pdf(pdf_path: str, max_pages: int = 50) -> list:
        """
        Extrae contenido estructurado de un PDF usando Vision LLM.
        Retorna una lista de elementos por página.
        """
        print(f"👁️ [Nodo ExtractOCR]: Iniciando extracción visual: {pdf_path}")
        
        # Instanciar el proveedor basado en la configuración del prompt
        proveedor = AIProviderFactory.get_provider(AI_CONFIG)
        
        doc = fitz.open(pdf_path)
        extracted_elements = []  # Lista plana de todos los elementos encontrados
        
        # Procesamos todas las páginas requeridas
        pages_to_process = range(min(max_pages, len(doc)))
        
        for i in pages_to_process:
            print(f"   -> Procesando página {i + 1}...")
            try:
                # 1. Obtener imagen de la página
                img_bytes = extract_page_image(pdf_path, i)
                
                # 2. Mejorar contraste (binarización)
                img_bytes = enhance_image_contrast(img_bytes)
                
                # 3. Codificar a Base64
                base64_image = base64.b64encode(img_bytes).decode('utf-8')
                
                # 4. Llamada a IA a través del Factory
                system_prompt = "Devuelve un JSON con los elementos extraídos."
                elementos, raw_response, tokens_in, tokens_out = proveedor.analyze_image(
                    image_b64=base64_image,
                    prompt=EXTRACT_TEXT_PROMPT,
                    system_prompt=system_prompt,
                    config=AI_CONFIG
                )
                
                # Resumen de elementos
                type_counts = {}
                for el in elementos:
                    t = el.get("type", "unknown")
                    type_counts[t] = type_counts.get(t, 0) + 1
                
                print(f"      ✅ Elementos encontrados: {len(elementos)} {type_counts}")
                
                # 5. Enriquecer elementos con metadatos de página
                for idx, el in enumerate(elementos):
                    el["pagina"] = i + 1
                    el["pdf_path"] = pdf_path
                    el["element_index"] = idx
                    extracted_elements.append(el)
                    
            except Exception as e:
                print(f"❌ Error procesando página {i+1}: {e}")
                # En caso de error, podríamos agregar un elemento de error o continuar
        
        doc.close()
        return extracted_elements

