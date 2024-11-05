from ..documentation.rag_system import TableRAG
from ..documentation.pdf_reader import PDFReader
from ..subschema.schema_extractor import SchemaExtractor

class DocumentationPipeline:
    def __init__(self, pdf_path, embedding_handler, db_file):
        self.pdf_path = pdf_path
        self.embedding_handler = embedding_handler
        self.pdf_reader = PDFReader(self.pdf_path)

        # Initialize SchemaExtractor and extract schema
        self.schema_extractor = SchemaExtractor(db_file, self.embedding_handler)
        schema = self.schema_extractor.extract_schema_from_db()

        # Process and embed documentation via TableRAG with schema information
        documentation = self.extract_documentation()
        self.table_rag = TableRAG(self.embedding_handler, documentation, schema)

    def extract_documentation(self):
        print("Extracting documentation from PDF...")
        documentation = self.pdf_reader.extract_sections()
        return documentation

    def retrieve_relevant_tables(self, query):
        # Use TableRAG to find relevant tables based on the user query
        relevant_tables = self.table_rag.find_relevant_tables(query)
        print("Relevant Tables from Documentation:", relevant_tables)
        return relevant_tables
