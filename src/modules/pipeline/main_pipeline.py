import os
import sqlite3
import pandas as pd
from ..embedding_handler import EmbeddingHandler
from ..documentation.rag_system import RAGSystem
from ..llm import LLM
from .subschema_pipeline import SubschemaPipeline  
from .documentation_pipeline import DocumentationPipeline  

class Pipeline:
    def __init__(self, db_file, user_query, pdf_path, output_dir='./data'):
        self.db_file = os.path.abspath(db_file)
        self.user_query = user_query
        self.output_dir = output_dir

        # Initialize components
        self.embedding_handler = EmbeddingHandler(output_dir=self.output_dir)
        self.llm = LLM()
        
        # Initialize documentation pipeline
        self.documentation_pipeline = DocumentationPipeline(pdf_path, self.embedding_handler)
        self.rag_system = RAGSystem(self.embedding_handler, self.documentation_pipeline.extract_documentation())
        
        # Initialize subschema pipeline
        self.subschema_pipeline = SubschemaPipeline(self.db_file, self.embedding_handler)

    def run(self):
        """Run the entire pipeline."""
        # Retrieve relevant documents
        relevant_docs = self.rag_system.retrieve_relevant_docs(self.user_query)
        
        # Extract schema and foreign keys
        schema, foreign_keys = self.subschema_pipeline.extract_schema_and_foreign_keys()

        # Extract keywords
        keywords = self.subschema_pipeline.extract_keywords(self.user_query)

        # Map keywords to schema and find valid joins
        relevant_columns, joins = self.subschema_pipeline.map_keywords_to_schema(schema, foreign_keys, keywords)

        # Generate the SQL query
        sql_query = self.generate_sql(relevant_columns, joins, relevant_docs)

        # Execute the SQL query
        result_df = self.execute_sql(sql_query)

        # Analyze the result
        analysis = self.llm.analyze_result(self.user_query, result_df)

        return analysis

    def generate_sql(self, relevant_columns, joins, relevant_docs):
        print("Generating SQL query with LLM...")
        column_documentation_matches = {col: [(col, 1.0)] for col in relevant_columns}
        sql_query = self.llm.generate_sql_with_rag(self.user_query, relevant_columns, joins, column_documentation_matches, relevant_docs)
        print(f"Generated SQL Query:\n{sql_query}")
        return sql_query

    def execute_sql(self, sql_query):
        print("Executing SQL query...")
        conn = sqlite3.connect(self.db_file)
        try:
            df = pd.read_sql_query(sql_query, conn)
            if df is not None and not df.empty:
                print("\nSQL Query Results (Pandas DataFrame):")
                print(df.to_string(index=False))
            else:
                print("No results returned from the SQL query.")
            return df
        except Exception as e:
            print(f"Error executing query: {e}\nQuery: {sql_query}")
            return None
        finally:
            conn.close()
