import fitz  # PyMuPDF

class ExtractStandardService:
    @staticmethod
    def extract_from_pdf(pdf_path: str) -> list:
        """
        Extrae texto de un PDF digital directamente (sin OCR).
        """
        print(f"📄 Extrayendo texto estándar: {pdf_path}")
        
        doc = fitz.open(pdf_path)
        pages_content = []
        
        for i, page in enumerate(doc):
            text = page.get_text()
            if text.strip():  # Solo agregamos si hay texto
                pages_content.append({
                    "page": i + 1,
                    "text": text
                })
        
        doc.close()
        return pages_content
