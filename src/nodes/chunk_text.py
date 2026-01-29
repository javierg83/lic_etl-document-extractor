from langchain_text_splitters import RecursiveCharacterTextSplitter

class ChunkTextNode:
    @staticmethod
    def execute(state: dict) -> dict:
        try:
            return ChunkTextNode._run(state)
        except Exception as e:
            state["status"] = "failed"
            state["error_node"] = "chunk_text"
            state["error"] = str(e)
            print(f"❌ Error en ChunkTextNode: {e}")
            return state

    @staticmethod
    def _run(state: dict) -> dict:
        pages_content = state.get("pages_content", [])
        toc = state.get("toc", {}).get("structure", [])
        
        print(f"✂️ Dividiendo texto en fragmentos. Páginas a procesar: {len(pages_content)}")
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100,
            separators=["\n\n", "\n", " ", ""]
        )
        
        all_chunks = []
        for page_data in pages_content:
            page_num = page_data["page"]
            text = page_data["text"]
            
            # Determinar a qué capítulo y sub-capítulo pertenece esta página
            chapter_title = "Sin Sección"
            sub_chapter_title = ""
            
            for item in toc:
                if item["start_page"] <= page_num <= item["end_page"]:
                    chapter_title = item["chapter_title"]
                    # Buscar sub-capítulo dentro de este capítulo
                    for sub in item.get("sub_chapters", []):
                        if sub["start_page"] <= page_num <= sub["end_page"]:
                            sub_chapter_title = sub["title"]
                            break
                    break
            
            chunks = text_splitter.split_text(text)
            for chunk in chunks:
                all_chunks.append({
                    "text": chunk,
                    "page": page_num,
                    "chapter": chapter_title,
                    "sub_chapter": sub_chapter_title
                })
        
        state["chunks"] = all_chunks
        state["status"] = "ok"
        print(f"✅ Texto dividido en {len(all_chunks)} fragmentos.")
        
        return state
