import fitz

def extract_page_image(pdf_path: str, page_number: int, dpi: int = 200) -> bytes:
    """
    Extrae una página de un PDF como imagen (bytes PNG).
    """
    try:
        with fitz.open(pdf_path) as doc:
            if page_number < 0 or page_number >= len(doc):
                raise ValueError(f"Número de página {page_number} fuera de rango.")
            
            page = doc.load_page(page_number)
            pix = page.get_pixmap(dpi=dpi)
            return pix.tobytes("png")
    except Exception as e:
        print(f"Error extrayendo imagen de PDF: {e}")
        return b""
