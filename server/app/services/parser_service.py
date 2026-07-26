from pathlib import Path
from docling.document_converter import DocumentConverter


class ParserService:

    def __init__(self):
        self.converter = DocumentConverter()

    def parse_document(self, file_path: Path) -> str:
        result = self.converter.convert(file_path)

        document = result.document

        markdown = document.export_to_markdown()

        return markdown
