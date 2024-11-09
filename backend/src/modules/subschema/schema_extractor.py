import sqlite3
import os
import torch
from transformers import RobertaTokenizer, RobertaModel
from sklearn.metrics.pairwise import cosine_similarity
from ..other.keyword_extractor import KeywordExtractor


class SchemaExtractor:
    def __init__(self, db_file, embedding_handler, extract_method="roberta"):
        self.db_file = db_file
        self.embedding_handler = embedding_handler
        self.extract_method = extract_method

    def extract_keywords(self, query, similarity_threshold=0.7, window_size=4):
        extractor = KeywordExtractor(method=self.extract_method)
        return extractor.extract_keywords(query, similarity_threshold, window_size)

    def extract_schema_from_db(self):
        if not os.path.exists(self.db_file):
            raise ValueError(f"Database file not found: {self.db_file}")

        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()

            schema = {}
            if not tables:
                raise ValueError("No tables found in the database.")

            for table in tables:
                table_name = table[0]
                cursor.execute(f"PRAGMA table_info({table_name});")
                columns = cursor.fetchall()
                if columns:
                    schema[table_name] = [col[1] for col in columns]
                else:
                    print(f"Warning: No columns found for table {table_name}.")

            conn.close()
            return schema
        except Exception as e:
            print(f"An error occurred while extracting the schema: {e}")
        return None

    def extract_foreign_key_relations(self):
        if not os.path.exists(self.db_file):
            raise ValueError(f"Database file not found: {self.db_file}")

        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        foreign_keys = {}
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        for table in tables:
            table_name = table[0]
            cursor.execute(f"PRAGMA foreign_key_list({table_name});")
            keys = cursor.fetchall()
            for key in keys:
                foreign_keys.setdefault(table_name, []).append(
                    {
                        "from": key[3],  # Column in the current table
                        "to_table": key[2],  # Table it references
                        "to_column": key[4],  # Column in the referenced table
                    }
                )
        conn.close()
        return foreign_keys
