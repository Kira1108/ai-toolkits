from ai_toolkits.files.parse import MarkDownFileReader
from ai_toolkits.files.anchor import AnchorFinder
from ai_toolkits.files.recursive import langchain_recursive_chinese_split


class SemanticPipeline:
    def __init__(self, trim_long_chunks:bool = False):
        self.reader = MarkDownFileReader()
        self.anchor_finder = AnchorFinder()
        self.trim_long_chunks = trim_long_chunks
        
    async def split_text(self, text: str):
        response = await self.anchor_finder.run(text)
        for anchor in response.anchor_sentences:
            text = text.replace(anchor, f"<new-chunk>{anchor}")
        chunks = text.split("<new-chunk>")
        chunks = [chunk.strip() for chunk in chunks if len(chunk.strip()) > 0]
        
        if not self.trim_long_chunks:
            return chunks
        print("Trimming long chunks with recursive split...")
        trimmed_chunks = []
        for chunk in chunks:
            if len(chunk) > 1500:
                trimmed_chunks.extend(langchain_recursive_chinese_split(chunk, chunk_size=1000, chunk_overlap=100))
            else:
                trimmed_chunks.append(chunk)
        return trimmed_chunks

    async def split_file(self, file_path: str):
        doc_content = self.reader.read(file_path)
        chunks =await self.split_text(doc_content)
        return chunks
