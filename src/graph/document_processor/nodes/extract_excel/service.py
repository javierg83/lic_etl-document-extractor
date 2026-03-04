class ExtractExcelService:
    @staticmethod
    def extract_text(file_path: str) -> list:
        """
        Extrae contenido de un Excel y lo convierte a una representación textual (Markdown).
        """
        print(f"📊 Extrayendo Excel: {file_path}")
        
        import pandas as pd
        
        try:
            excel_file = pd.ExcelFile(file_path)
            sheet_names = excel_file.sheet_names
            
            pages_content = []
            
            for i, sheet_name in enumerate(sheet_names):
                # Leemos la hoja, rellenamos nulos con string vacío
                df = pd.read_excel(file_path, sheet_name=sheet_name).fillna("")
                
                # Convertimos DataFrame a tabla Markdown
                # markdown_table = df.to_markdown(index=False)
                
                # NADA de tabla gigante. Convertimos a lista de diccionarios, uno por fila.
                rows = df.to_dict(orient="records")
                
                row_texts = []
                for row_idx, row in enumerate(rows):
                    row_parts = []
                    for k, v in row.items():
                        if str(v).strip(): # Ignorar vacíos
                            row_parts.append(f"{k}: {v}")
                    if row_parts:
                        row_texts.append(", ".join(row_parts))
                
                pages_content.append({
                    "page": i + 1,
                    "sheet_name": sheet_name,
                    # "text": markdown_table, # Quitamos text gigante
                    "rows": row_texts, # Enviamos las filas formateadas
                    "origin": "excel" # Bandera especial
                })
                
            return pages_content
            
        except Exception as e:
            print(f"❌ Error al extraer texto de Excel: {e}")
            raise e
