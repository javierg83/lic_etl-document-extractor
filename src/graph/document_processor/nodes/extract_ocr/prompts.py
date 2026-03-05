AI_CONFIG = {
    "engine": "gemini",  # "openai" or "gemini"
    "model": "gemini-2.5-pro",   # gemini-2.5-pro or gemini-2.5-flash
    "temperature": 0.0
}

#AI_CONFIG = {
#    "engine": "openai",  # "openai" or "gemini"
#    "model": "gpt-4o",   # "gpt-4o", "gemini-1.5-pro", etc.
#    "temperature": 0.0
#}

EXTRACT_TEXT_PROMPT = """
You are an advanced document analysis AI. Your task is to analyze the image of a PDF page and extract its content in a structured JSON format.

Please identify and extract the following elements:
- "titles": Any headers or titles.
- "text": Standard paragraphs or blocks of text.
- "tables": Detect tables and extract their content as a 2D list (list of lists).
- "checkboxes": Detect checkboxes and their status (checked/unchecked) along with associated label.

Return a JSON object with a key "elements" containing a list of items. Each item should have:
- "type": One of "titulo", "texto", "tabla", "checkbox".
- "contenido": The content (string for text/titles, list of lists for tables, string with status for checkboxes).

Example format:
{
  "elements": [
    {"type": "titulo", "contenido": "Section 1"},
    {"type": "texto", "contenido": "This is a paragraph."},
    {"type": "tabla", "contenido": [["Col1", "Col2"], ["Val1", "Val2"]]}
  ]
}
"""
