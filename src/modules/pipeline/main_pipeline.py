import os
import sqlite3
import re
import pandas as pd
from ..embedding_handler import EmbeddingHandler
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
        
        # Initialize documentation and subschema pipelines
        self.documentation_pipeline = DocumentationPipeline(pdf_path, self.embedding_handler, db_file)
        self.subschema_pipeline = SubschemaPipeline(db_file, self.embedding_handler)

    def generate_sql(self, joins, relevant_tables):
        print("Generating SQL query with LLM...")

        # Prepare subschema context
        subschema_context = f"Tables: {', '.join(relevant_tables)}\nJoin Conditions:\n" + "\n".join(
            [f"{j['tables'][0]}.{j['columns'][0]} = {j['tables'][1]}.{j['columns'][1]}" for j in joins]
        )

        sql_query = self.llm.generate_sql_with_rag(
            self.user_query,
            joins,
            relevant_tables
        )
        return sql_query

    def execute_sql(self, sql_query):
        print("Executing SQL query...")
        conn = sqlite3.connect(self.db_file)
        try:
            df = pd.read_sql_query(sql_query, conn)
            if df is not None and not df.empty:
                print("\nSQL Query Results (Pandas DataFrame):")
                print(df.to_string(index=False))
                return df
            else:
                print("No results returned from the SQL query.")
                return df
        except Exception as e:
            print(f"Error executing query on first attempt: {e}\nQuery: {sql_query}")

            cleaned_sql_query = self.extract_sql_from_output(sql_query)
            if cleaned_sql_query:
                print("Retrying with cleaned SQL query...")
                try:
                    df = pd.read_sql_query(cleaned_sql_query, conn)
                    if df is not None and not df.empty:
                        print("\nSQL Query Results (Pandas DataFrame):")
                        print(df.to_string(index=False))
                    else:
                        print("No results returned from the cleaned SQL query.")
                    return df
                except Exception as e:
                    print(f"Error executing cleaned query: {e}\nCleaned Query: {cleaned_sql_query}")
                    return None
            else:
                print("No valid SQL could be extracted from the output.")
                return None
        finally:
            conn.close()

    def extract_sql_from_output(self, output_text):
        match = re.search(r"```sql\n(.*?)```", output_text, re.DOTALL)
        if match:
            extracted_sql = match.group(1).strip()
            print(f"Extracted SQL Query:\n{extracted_sql}")
            return extracted_sql
        else:
            print("No SQL code block found in the output.")
            return None

    def run(self):
        """Run the entire pipeline."""
        # Retrieve relevant tables based on the documentation
        doc_tables = self.documentation_pipeline.retrieve_relevant_tables(self.user_query)
        
        # Extract keywords and find additional tables based on schema mapping
        keywords = self.subschema_pipeline.extract_keywords(self.user_query)
        schema_tables = self.subschema_pipeline.identify_relevant_tables(keywords)

        # Combine all tables identified from documentation and schema mapping
        relevant_tables = list(set(doc_tables + schema_tables))
        print("Final List of Relevant Tables:", relevant_tables)

        # Generate joins between relevant tables
        joins = self.subschema_pipeline.create_joins(relevant_tables)

        # Generate the SQL query using tables and joins as subschema context
        sql_query = self.generate_sql(joins, relevant_tables)

        # Execute the SQL query
        result_df = self.execute_sql(sql_query)

        # Analyze the SQL and result
        analysis = self.llm.analyze_result(self.user_query, sql_query, result_df)

        return analysis
