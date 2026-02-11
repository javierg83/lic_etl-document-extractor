import fitz

class SplitterService:
    @staticmethod
    def identify_and_split(file_path: str, file_type: str = None):
        """
        Recibe el path y el tipo (ya detectado por ClassifyNode).
        Retorna una lista de sub-documentos (páginas, sheets, etc.)
        """
        # Fallback si no viene el tipo
        if not file_type:
             # Importación diferida o mover utils si fuera necesario, 
             # pero idealmente el nodo anterior ya lo hizo.
             print("⚠️ SplitterService: file_type no provisto, se asume PDF o se debería detectar.")
             file_type = 'pdf' # Default temporal
        
        if file_type == 'pdf':
            return SplitterService._split_pdf(file_path)
        elif file_type == 'excel':
            return SplitterService._split_excel(file_path)
        # elif file_type == 'word':
        #     return SplitterService._split_word(file_path)
        else:
            print(f"⚠️ Tipo de archivo no soportado o desconocido: {file_type}")
            return {
                "type": "unknown",
                "sub_documents": []
            }

    @staticmethod
    def _split_pdf(file_path: str):
        """
        Analiza un PDF. Por ahora NO separa físicamente en archivos, 
        sino que genera metadatos para cada página.
        """
        doc = fitz.open(file_path)
        total_pages = len(doc)
        
        # Detector rápido de escaneo (revisando primeras 3 páginas)
        is_scanned = True
        for i in range(min(3, total_pages)):
            text = doc[i].get_text().strip()
            if len(text) > 50:
                is_scanned = False
                break
        doc.close()
        
        # Generamos una lista de "tareas" por página
        sub_documents = []
        for i in range(total_pages):
            sub_documents.append({
                "type": "page",
                "page_number": i + 1,
                "source_file": file_path,
                "is_scanned": is_scanned, 
                # En el futuro, aquí podría ir la imagen base64 si hiciéramos el split real aquí
            })
            
        return {
            "type": "pdf",
            "is_scanned": is_scanned,
            "total_pages": total_pages,
            "sub_documents": sub_documents
        }

    @staticmethod
    def _split_excel(file_path: str):
        """
        Placeholder para lógica de Excel
        """
        return {
            "type": "excel",
            "sub_documents": [
                {"type": "sheet", "sheet_name": "Sheet1", "source_file": file_path}
            ]
        }
