# Archivos Deprecados (Para borrar en el futuro)

Estos archivos han sido reemplazados por la nueva arquitectura en `src/graph/document_processor/nodes/` y ya no son utilizados por el grafo principal.

## En `src/nodes/`
- src/nodes/classify_pdf.py
- src/nodes/extract_text_ocr.py
- src/nodes/extract_text_standard.py
- src/nodes/chunk_text.py
- src/nodes/generate_embeddings.py
- src/nodes/save_to_redis.py

## En `src/graph/document_processor/node/` (Antiguos Wrappers)
- src/graph/document_processor/node/classify_node.py
- src/graph/document_processor/node/extract_ocr_node.py
- src/graph/document_processor/node/extract_standard_node.py
- src/graph/document_processor/node/chunking_node.py
- src/graph/document_processor/node/embeddings_node.py
- src/graph/document_processor/node/save_node.py

## Notas
- El grafo principal `src/graph/document_processor/graph.py` ya apunta exclusivamente a las nuevas ubicaciones.
- Se recomienda borrar estos archivos una vez que la verificación completa en entorno de producción haya sido exitosa.
