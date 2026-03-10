import base64
import json
import fitz
from src.services.ai_engine.factory import AIProviderFactory
from .prompts import EXTRACT_TEXT_PROMPT, AI_CONFIG
from src.utils.image_filters import enhance_image_contrast
from src.utils.pdf_utils import extract_page_image

class ExtractOcrService:
    @staticmethod
    def extract_from_pdf(pdf_path: str, licitacion_id: str = "default", max_pages: int = 50, tipo_adquisicion: str = "LICITACION_PUBLICA") -> list:
        """
        Extrae contenido estructurado de un PDF usando Vision LLM.
        Retorna una lista de elementos por página.
        """
        print(f"👁️ [Nodo ExtractOCR]: Iniciando extracción visual: {pdf_path} (Modo: {tipo_adquisicion})")
        
        # Instanciar el proveedor basado en la configuración del prompt
        proveedor = AIProviderFactory.get_provider(AI_CONFIG)
        
        doc = fitz.open(pdf_path)
        extracted_elements = []  # Lista plana de todos los elementos encontrados
        
        # Seleccionar prompt base
        from .prompts import EXTRACT_TEXT_PROMPT, EXTRACT_TABLE_AGIL_PROMPT
        base_prompt = EXTRACT_TABLE_AGIL_PROMPT if tipo_adquisicion == "COMPRA_AGIL" else EXTRACT_TEXT_PROMPT
        
        # Procesamos todas las páginas requeridas
        pages_to_process = range(min(max_pages, len(doc)))
        
        previous_table_headers = None
        
        for i in pages_to_process:
            print(f"   -> Procesando página {i + 1}...")
            try:
                # 1. Obtener imagen de la página
                img_bytes = extract_page_image(pdf_path, i)
                
                # 2. Mejorar contraste (binarización)
                img_bytes = enhance_image_contrast(img_bytes)
                
                # 3. Codificar a Base64
                base64_image = base64.b64encode(img_bytes).decode('utf-8')
                
                # Preparar prompt dinámico con memoria de la página anterior
                active_prompt = base_prompt
                if tipo_adquisicion == "COMPRA_AGIL" and previous_table_headers:
                    active_prompt += f"\n\nCONTEXT FROM PREVIOUS PAGE:\nThe table on the previous page had these headers: {previous_table_headers}. If you find a continuation of this table on this page without headers, force the extracted table to use these exact same headers (as the first row) and align the data accordingly to maintain structural consistency!"

                # 4. Llamada a IA a través del Factory
                system_prompt = "Devuelve un JSON con los elementos extraídos."
                elementos, raw_response, tokens_in, tokens_out = proveedor.analyze_image(
                    image_b64=base64_image,
                    prompt=active_prompt,
                    system_prompt=system_prompt,
                    config=AI_CONFIG
                )
                
                # Guardar memoria de cabeceras de tabla para la SIGUIENTE página
                if tipo_adquisicion == "COMPRA_AGIL":
                    for el in reversed(elementos):
                        if el.get("type") == "tabla" and isinstance(el.get("contenido"), list) and len(el.get("contenido")) > 0:
                            # Asumimos que la primera fila estructural de la última tabla es la cabecera
                            previous_table_headers = el.get("contenido")[0]
                            break
                            
                # Resumen de elementos
                type_counts = {}
                for el in elementos:
                    t = el.get("type", "unknown")
                    type_counts[t] = type_counts.get(t, 0) + 1
                
                print(f"      ✅ Elementos encontrados: {len(elementos)} {type_counts}")
                
                # Enviar métricas al backend
                from src.utils.metrics import log_ai_usage
                model_name = AI_CONFIG.get("model", "gpt-4o")
                provider_name = AI_CONFIG.get("provider", "openai")
                log_ai_usage(
                    licitacion_id=licitacion_id, 
                    action="EXTRACCION_TEXTO_OCR", 
                    provider=provider_name, 
                    model=model_name, 
                    input_tokens=tokens_in, 
                    output_tokens=tokens_out
                )

                # 5. Enriquecer elementos con metadatos de página
                for idx, el in enumerate(elementos):
                    el["pagina"] = i + 1
                    el["pdf_path"] = pdf_path
                    el["element_index"] = idx
                    extracted_elements.append(el)
                    
                # [DEBUG] Guardar la extracción visual para depuración
                try:
                    import os
                    debug_dir = os.path.join(os.getcwd(), "debug_ocr")
                    os.makedirs(debug_dir, exist_ok=True)
                    debug_file = os.path.join(debug_dir, f"ocr_page_{i+1}.json")
                    with open(debug_file, "w", encoding="utf-8") as df:
                        json.dump(elementos, df, indent=2, ensure_ascii=False)
                except Exception as ex_dbg:
                    print(f"Error escribiendo debug ocr json: {ex_dbg}")
                    
            except Exception as e:
                print(f"❌ Error procesando página {i+1}: {e}")
                # En caso de error, podríamos agregar un elemento de error o continuar
        
        doc.close()
        return extracted_elements

