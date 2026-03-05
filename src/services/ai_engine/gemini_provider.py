from .base import BaseAIProvider
from typing import Dict, Any, Tuple
import google.generativeai as genai
import json
import re
import time

class GeminiProvider(BaseAIProvider):
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)

    def generate_text(self, prompt: str, system_prompt: str, config: Dict[str, Any]) -> Tuple[str, Dict[str, int]]:
        model_name = config.get("model", "gemini-1.5-pro")
        temperature = config.get("temperature", 0.0)
        
        generation_config = {
            "temperature": temperature,
        }

        model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=system_prompt
        )

        print(f"[GeminiProvider] 🚀 Enviando solicitud a {model_name}...")
        response = model.generate_content(
            prompt,
            generation_config=generation_config
        )

        reply = response.text
        
        usage = {
            "input": 0, 
            "output": 0
        }
        if hasattr(response, 'usage_metadata'):
             usage["input"] = response.usage_metadata.prompt_token_count
             usage["output"] = response.usage_metadata.candidates_token_count

        return reply, usage

    def analyze_image(self, image_b64: str, prompt: str, system_prompt: str, config: Dict[str, Any]) -> Tuple[Any, str, int, int]:
        model_name = config.get("model", "gemini-1.5-pro")
        temperature = config.get("temperature", 0.0)

        # Gemini necesita la imagen decodificada como objeto blob o similar
        # "mime_type": "image/jpeg", "data": ...
        
        model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=system_prompt
        )
        
        print(f"[GeminiProvider] 🚀 Enviando imagen a {model_name}...")
        
        # En Google GenAI SDK, pasamos un diccionario simple para blob
        # Asumimos PNG u otra imagen compatible con Base64 procesada por PyMuPDF
        image_part = {
            "mime_type": "image/png", 
            "data": image_b64 
        }

        # Retry logic for 429 Quota Exceeded (Opcional, pero recomendado con Gemini)
        max_retries = 3
        base_delay = 5 # seconds
        
        response = None
        for attempt in range(max_retries + 1):
            try:
                # Importante requerir JSON en Gemini pasandole el tipo mime
                # y asegurándonos de que en el prompt se pide json
                response = model.generate_content(
                    [prompt, image_part],
                    generation_config={
                        "temperature": temperature,
                        "response_mime_type": "application/json" if "json" in prompt.lower() or "json" in system_prompt.lower() else "text/plain"
                    }
                )
                break # Success
            except Exception as e:
                # Check for 429 or quota related errors
                error_str = str(e)
                if "429" in error_str or "quota" in error_str.lower():
                    if attempt < max_retries:
                        delay = base_delay * (2 ** attempt) + 1 # Exponential: 5+1, 10+1, 20+1 ...
                        print(f"[GeminiProvider] ⏳ Quota exceeded (429). Retrying in {delay}s... (Attempt {attempt+1}/{max_retries})")
                        time.sleep(delay)
                        continue
                    else:
                        print(f"[GeminiProvider] ❌ Max retries reached for 429 error.")
                        raise e
                else:
                    raise e
                    
        if not response:
            raise Exception("[GeminiProvider] No response received from Gemini.")

        raw = response.text
        
        # Limpieza básica
        raw = re.sub(r"^```(?:json)?\s*", "", raw, flags=re.MULTILINE)
        raw = re.sub(r"\s*```$", "", raw, flags=re.MULTILINE)

        tokens_in = 0
        tokens_out = 0
        if hasattr(response, 'usage_metadata'):
             tokens_in = response.usage_metadata.prompt_token_count
             tokens_out = response.usage_metadata.candidates_token_count

        elementos = []
        try:
            data = json.loads(raw)
            elementos = data.get('elements', data.get('elementos', []))
        except json.JSONDecodeError:
             print(f"[GeminiProvider] ⚠️ JSON inválido en respuesta.")

        return elementos, raw, tokens_in, tokens_out
