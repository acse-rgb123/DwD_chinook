from ..documentation.rag_system import RAGSystem  # Import RAGSystem
from ..documentation.pdf_reader import PDFReader  # Import PDFReader

class DocumentationPipeline:
    def __init__(self, pdf_path, embedding_handler):
        self.pdf_path = pdf_path
        self.embedding_handler = embedding_handler
        self.pdf_reader = PDFReader(self.pdf_path)
        
        # Process and embed documentation via RAGSystem
        documentation = self.extract_documentation()
        self.rag_system = RAGSystem(self.embedding_handler, documentation)

    def extract_documentation(self):
        print("Extracting documentation from PDF...")
        documentation = self.pdf_reader.extract_sections()
        return documentation

    def retrieve_relevant_chunks(self, query, similarity_threshold=0.45):
        # Retrieve relevant chunks from RAGSystem
        relevant_chunks = self.rag_system.retrieve_relevant_docs(query, similarity_threshold)
        return relevant_chunks

