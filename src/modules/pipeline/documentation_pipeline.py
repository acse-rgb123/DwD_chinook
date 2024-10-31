from ..documentation.pdf_reader import PDFReader

class DocumentationPipeline:
    def __init__(self, pdf_path, embedding_handler):
        self.pdf_path = pdf_path
        self.embedding_handler = embedding_handler
        self.pdf_reader = PDFReader(self.pdf_path)

    def extract_documentation(self):
        print("Extracting documentation from PDF...")
        documentation = self.pdf_reader.extract_sections()
        return documentation
