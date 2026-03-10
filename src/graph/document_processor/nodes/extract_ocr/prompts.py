AI_CONFIG = {
    "engine": "gemini",  # "openai" or "gemini"
    "model": "gemini-2.5-pro",   # gemini-2.5-pro or gemini-2.5-flash
    "temperature": 0.0
}

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

EXTRACT_TABLE_AGIL_PROMPT = """
You are an expert procurement document AI. You are looking at a "Compra Agil" (Fast Purchase) or a Direct Quote.
These documents usually feature strict tables or visual bounding boxes denoting a list of products to acquire.

Your CRITICAL TASK is to prevent item fragmentation. DO NOT extract individual table cells as separate "texto" elements.
Instead, detect the main product table and extract it as a single cohesive "tabla" element, ensuring product codes, names, quantities, and descriptions remain row-aligned in a 2D list.
IMPORTANT: If a table spans multiple pages, it might not have column headers on the subsequent pages. If you see a grid of items that looks like a continuation of a table, STILL extract it as a "tabla" element.

Return a JSON object with a key "elements" containing a list of items.
Example format:
{
  "elements": [
    {"type": "titulo", "contenido": "Orden de Compra Agil 12345"},
    {"type": "tabla", "contenido": [["Codigo", "Producto", "Cantidad", "Descripcion"], ["123", "Papel", "2", "Resma A4"]]}
  ]
}
"""
