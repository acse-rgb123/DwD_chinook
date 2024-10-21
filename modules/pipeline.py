import os
import sqlite3
import pandas as pd
import networkx as nx
from .embedding_handler import EmbeddingHandler
from .rag_system import RAGSystem
from .pdf_reader import PDFReader
from .schema_mapper import SchemaMapper
from .llm import LLM
from .schema_extractor import SchemaExtractor

class Pipeline:
    def __init__(self, db_file, user_query, pdf_path):
        self.db_file = os.path.abspath(db_file)
        self.user_query = user_query
        self.pdf_path = os.path.abspath(pdf_path)

        self.embedding_handler = EmbeddingHandler()

        # PDF Reader for extracting documentation
        self.pdf_reader = PDFReader(self.pdf_path)
        documentation = self.pdf_reader.extract_sections()

        # RAG system for document retrieval
        self.rag_system = RAGSystem(self.embedding_handler, documentation)

        # Initialize LLM for SQL generation
        self.llm = LLM()

        # Initialize Schema and Keyword Extraction
        self.schema_extractor = SchemaExtractor(self.db_file, self.embedding_handler)

    def extract_schema_and_foreign_keys(self):
        print("Extracting schema and foreign key relationships...")
        schema = self.schema_extractor.extract_schema_from_db()
        if not schema:
            raise ValueError("Schema extraction failed.")
        
        foreign_keys = self.schema_extractor.extract_foreign_key_relations()
        if not foreign_keys:
            raise ValueError("Foreign key extraction failed.")
        
        return schema, foreign_keys

    def extract_keywords(self):
        print("Extracting keywords using RoBERTa...")
        keywords = self.schema_extractor.extract_keywords_with_roberta(self.user_query)
        print(f"Extracted Keywords:\n{pd.Series(keywords)}")
        return keywords

    def map_keywords_to_schema(self, schema, foreign_keys, keywords):
        print("Mapping keywords to schema and creating subgraph with valid joins...")
        schema_mapper = SchemaMapper(schema, foreign_keys, self.embedding_handler)
        
        # Identify relevant tables first
        relevant_tables = schema_mapper.identify_relevant_tables(keywords)
        
        # Map keywords to columns using identified relevant tables
        mapped_columns = schema_mapper.map_keywords_to_columns(keywords, relevant_tables)

        # Create a placeholder for subgraph and join paths
        subgraph = nx.Graph()  # Initialize an empty graph for the subgraph
        join_paths = []  # Placeholder for join paths logic

        # Get table connections from mapped columns
        connections = schema_mapper.find_table_connections(relevant_tables)
        
        # Print relevant outputs
        print("\nTable Connections:")
        for connection in connections:
            print(f"{connection[0]} <-> {connection[1]} (From: {connection[2]['from_column']}, To: {connection[2]['to_column']})")

        # Create subgraph from the connections
        for connection in connections:
            subgraph.add_edge(connection[0], connection[1], from_column=connection[2]['from_column'], to_column=connection[2]['to_column'])

        print("\nSubschema Nodes:")
        print(subgraph.nodes())
        
        print("\nSubschema Edges (Foreign Key Joins with Column Info):")
        for edge in subgraph.edges(data=True):
            print(f"{edge[0]} <-> {edge[1]} (From: {edge[2]['from_column']}, To: {edge[2]['to_column']})")

        # Assuming you have logic to find join paths here
        # Replace the following with actual logic for finding join paths based on the subgraph
        join_paths = schema_mapper.find_paths_between_tables(subgraph, start_table="Customer")

        print("\nJoin Paths:")
        for path in join_paths:
            for join in path:
                print(f"{join['tables'][0]} -> {join['tables'][1]} (From: {join['columns'][0]}, To: {join['columns'][1]})")

        return mapped_columns, join_paths  # Adjusted return statement to include mapped_columns and join_paths


    def generate_sql(self, relevant_columns, joins, relevant_docs):
        print("Generating SQL query with LLM...")
        column_documentation_matches = {col: [(col, 1.0)] for col in relevant_columns}
        sql_query = self.llm.generate_sql_with_rag(self.user_query, relevant_columns, joins, column_documentation_matches, relevant_docs)
        print(f"Generated SQL Query:\n{sql_query}")
        return sql_query

    def execute_sql(self, sql_query):
        print("Executing SQL query...")

        if not os.path.exists(self.db_file):
            raise FileNotFoundError(f"Database file not found: {self.db_file}")

        conn = sqlite3.connect(self.db_file)
        try:
            df = pd.read_sql_query(sql_query, conn)
            if df is not None:
                print("\nSQL Query Results (Pandas DataFrame):")
                display(df)  # This will display the DataFrame in a Jupyter notebook format
            else:
                print("No results returned from the SQL query.")
            return df
        except Exception as e:
            print(f"Error executing query: {e}\nQuery: {sql_query}")
            return None
        finally:
            conn.close()

    def analyze_result(self, result_df):
        print("Analyzing result with LLM...")
        analysis = self.llm.analyze_result(self.user_query, result_df)
        print("\nAnalysis:")
        print(analysis)
        return analysis

    def run(self):
        relevant_docs = self.rag_system.retrieve_relevant_docs(self.user_query)
        
        schema, foreign_keys = self.extract_schema_and_foreign_keys()

        keywords = self.extract_keywords()

        relevant_columns, joins = self.map_keywords_to_schema(schema, foreign_keys, keywords)

        sql_query = self.generate_sql(relevant_columns, joins, relevant_docs)

        result_df = self.execute_sql(sql_query)

        analysis = self.analyze_result(result_df)

        return analysis
