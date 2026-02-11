import mimetypes
import os

def detect_file_type(file_path: str) -> str:
    """
    Detecta el tipo de archivo basado en la extensión o contenido.
    Retorna: 'pdf', 'excel', 'word', o 'unknown'
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
        
    mime, _ = mimetypes.guess_type(file_path)
    extension = os.path.splitext(file_path)[1].lower()
    
    if extension == '.pdf' or mime == 'application/pdf':
        return 'pdf'
    elif extension in ['.xlsx', '.xls', '.csv'] or mime in ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/vnd.ms-excel', 'text/csv']:
        return 'excel'
    elif extension in ['.docx', '.doc'] or mime in ['application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/msword']:
        return 'word'
        
    return 'unknown'
