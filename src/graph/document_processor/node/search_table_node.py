import json
import psycopg2
from openai import OpenAI
from src.config import (
    OPENAI_API_KEY, 
    DB_POSTGRES_NAME, DB_POSTGRES_USER, DB_POSTGRES_PASSWORD, DB_POSTGRES_HOST, DB_POSTGRES_PORT
)

class SearchTableNode:
    """
    Nodo que utiliza un LLM para identificar el índice de contenidos (ToC)
    y extraer la estructura de capítulos con sus rangos de páginas.
    Luego guarda esta estructura en la base de datos asociada al documento.
    """
    @staticmethod
    def execute(state: dict) -> dict:
        """
        Orquestador del nodo.
        Maneja errores y garantiza que el grafo reciba un state consistente.
        """
        try:
            return SearchTableNode._run(state)
        except Exception as e:
            state["status"] = "failed"
            state["error_node"] = "search_table"
            state["error"] = str(e)
            print(f"❌ Error en SearchTableNode: {e}")
            return state

    @staticmethod
    def _run(state: dict) -> dict:
        pages_content = state.get("pages_content", [])
        total_pages = state.get("total_pages", 0)
        doc_id = state.get("doc_id")
        
        if not pages_content:
            print("⚠️ No hay contenido de páginas para analizar el índice.")
            return state

        print("🔍 Analizando las primeras páginas para encontrar el índice...")
        
        # Tomamos las primeras 10 páginas para buscar el índice
        search_range = pages_content[:10]
        context_text = ""
        for p in search_range:
            context_text += f"--- PÁGINA {p['page']} ---\n{p['text']}\n\n"

        client = OpenAI(api_key=OPENAI_API_KEY)
        
        prompt = f"""
        Analiza el siguiente texto de las primeras páginas de un libro y encuentra el índice de contenidos (Table of Contents).
        
        Debes extraer una estructura jerárquica que incluya:
        1. El número de página donde se encuentra el índice físico (`index_page`).
        2. Los nombres de los CAPÍTULOS PRINCIPALES (`chapter_title`).
        3. Los SUB-CAPÍTULOS o SECCIONES importantes dentro de cada capítulo (`sub_chapters`).
        4. Calcular el rango de páginas (`start_page` y `end_page`) para cada nivel. 
           - El 'end_page' de una sección es la página anterior al inicio de la siguiente sección (ya sea sub-capítulo o capítulo). 
           - Para la última sección del libro, el 'end_page' es {total_pages}.

        IMPORTANTE: Devuelve ÚNICAMENTE un objeto JSON estrictamente formateado como el siguiente ejemplo:
        {{
          "index_page": 3,
          "structure": [
            {{
              "chapter_title": "Introducción",
              "start_page": 6,
              "end_page": 20,
              "sub_chapters": [
                {{ "title": "Contexto", "start_page": 6, "end_page": 12 }},
                {{ "title": "Objetivos", "start_page": 13, "end_page": 20 }}
              ]
            }},
            {{
              "chapter_title": "El Ciclo Scrum",
              "start_page": 21,
              "end_page": 44,
              "sub_chapters": []
            }}
          ]
        }}

        Si no encuentras sub-capítulos para un capítulo, deja la lista "sub_chapters" vacía [].
        Si no encuentras un índice en absoluto, devuelve un objeto con "structure": [].

        TEXTO A ANALIZAR:
        {context_text}
        """

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Eres un asistente experto en análisis de documentos PDF y extracción de metadatos estructurados."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            response_format={ "type": "json_object" }
        )

        try:
            toc_data = json.loads(response.choices[0].message.content)
            state["toc"] = toc_data
            print(f"✅ Índice extraído: {len(toc_data.get('structure', []))} capítulos encontrados.")
            
            # Guardar en la base de datos si tenemos doc_id
            if doc_id and toc_data.get("structure"):
                SearchTableNode._save_to_db(doc_id, toc_data["structure"])
                
        except Exception as e:
            print(f"⚠️ Error al procesar el TOC o guardar en DB: {e}")
            state["toc"] = {"index_page": None, "structure": []}

        state["status"] = "ok"
        return state

    @staticmethod
    def _save_to_db(doc_id: int, structure: list):
        try:
            conn = psycopg2.connect(
                dbname=DB_POSTGRES_NAME,
                user=DB_POSTGRES_USER,
                password=DB_POSTGRES_PASSWORD,
                host=DB_POSTGRES_HOST,
                port=DB_POSTGRES_PORT
            )
            cursor = conn.cursor()
            
            # Limpiar TOC anterior para este documento si existe
            cursor.execute("DELETE FROM tabla_contenidos WHERE documento_id = %s", (doc_id,))
            
            for chapter in structure:
                # Insertar capítulo principal (nivel 0)
                cursor.execute("""
                    INSERT INTO tabla_contenidos (documento_id, titulo, pagina_inicio, pagina_fin, id_padre, nivel)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (doc_id, chapter["chapter_title"], chapter["start_page"], chapter["end_page"], None, 0))
                
                parent_id = cursor.fetchone()[0]
                
                # Insertar sub-capítulos (nivel 1)
                for sub in chapter.get("sub_chapters", []):
                    cursor.execute("""
                        INSERT INTO tabla_contenidos (documento_id, titulo, pagina_inicio, pagina_fin, id_padre, nivel)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (doc_id, sub["title"], sub["start_page"], sub["end_page"], parent_id, 1))
            
            conn.commit()
            conn.close()
            print(f"💾 Tabla de contenidos guardada en DB para el documento ID: {doc_id}")
        except Exception as e:
            print(f"❌ Error guardando TOC en DB: {e}")
            raise e
