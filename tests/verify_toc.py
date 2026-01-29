import sqlite3
import sys
import os

# Añadir el directorio raíz al path para importar src
sys.path.append(os.getcwd())

from src.nodes.search_table_contents import SearchTableContentsNode
from src.config import DB_PATH

def test_toc_storage():
    print("🧪 Iniciando prueba de almacenamiento de TOC...")
    
    # 1. Crear documento ficticio
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO documentos (filename, upload_date, checksum, size, estado) 
        VALUES (?, datetime('now'), ?, ?, ?)
    """, ("test_book.pdf", "abc123test", 1024, "procesando"))
    doc_id = cursor.lastrowid
    conn.commit()
    print(f"✅ Documento de prueba creado con ID: {doc_id}")

    # 2. Mockear datos del TOC
    mock_structure = [
        {
            "chapter_title": "Capítulo 1: Introducción",
            "start_page": 1,
            "end_page": 10,
            "sub_chapters": [
                {"title": "1.1 Contexto", "start_page": 1, "end_page": 5},
                {"title": "1.2 Objetivos", "start_page": 6, "end_page": 10}
            ]
        },
        {
            "chapter_title": "Capítulo 2: Desarrollo",
            "start_page": 11,
            "end_page": 20,
            "sub_chapters": []
        }
    ]

    # 3. Llamar al método de guardado directamente para la prueba
    try:
        SearchTableContentsNode._save_to_db(doc_id, mock_structure)
        print("✅ Método _save_to_db ejecutado.")
    except Exception as e:
        print(f"❌ Error al ejecutar _save_to_db: {e}")
        return

    # 4. Verificar en base de Datos
    cursor.execute("SELECT * FROM tabla_contenidos WHERE documento_id = ?", (doc_id,))
    rows = cursor.fetchall()
    
    print(f"📊 Registros encontrados en DB: {len(rows)}")
    for row in rows:
        print(f"  - {row}")

    # Verificaciones básicas
    assert len(rows) == 4, f"Se esperaban 4 registros, se encontraron {len(rows)}"
    
    # Limpiar
    cursor.execute("DELETE FROM tabla_contenidos WHERE documento_id = ?", (doc_id,))
    cursor.execute("DELETE FROM documentos WHERE id = ?", (doc_id,))
    conn.commit()
    conn.close()
    
    print("🚀 Prueba finalizada con ÉXITO.")

if __name__ == "__main__":
    test_toc_storage()
