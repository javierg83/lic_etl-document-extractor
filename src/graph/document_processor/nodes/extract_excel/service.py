class ExtractExcelService:
    @staticmethod
    def extract_text(file_path: str) -> list:
        """
        Extrae contenido de un Excel y lo convierte a una representación textual.
        Por ahora es un placeholder.
        """
        print(f"📊 Extrayendo Excel: {file_path}")
        
        # TODO: Implementar lógica real con Pandas/OpenPyXL
        # Retornar lista de dicts compatible con 'pages_content' aunque sean sheets
        return [
            {
                "page": 1,
                "sheet_name": "Sheet1",
                "text": "Contenido simulado de Excel: Fila 1 | Col A | Col B..."
            }
        ]
