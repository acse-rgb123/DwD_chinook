import sqlite3
import os
import torch
from transformers import RobertaTokenizer, RobertaModel
from sklearn.metrics.pairwise import cosine_similarity

class SchemaExtractor:
    def __init__(self, db_file, embedding_handler):
        self.db_file = db_file
        self.embedding_handler = embedding_handler
        self.tokenizer = RobertaTokenizer.from_pretrained('roberta-base')
        self.model = RobertaModel.from_pretrained('roberta-base', add_pooling_layer=False)

    def extract_keywords_with_roberta(self, query, similarity_threshold=0.2, window_size=3):
        inputs = self.tokenizer(query, return_tensors="pt")
        with torch.no_grad():
            outputs = self.model(**inputs)
            token_embeddings = outputs.last_hidden_state.squeeze(0)

        tokens = self.tokenizer.convert_ids_to_tokens(inputs['input_ids'][0])
        query_embedding = token_embeddings.mean(dim=0).unsqueeze(0)
        similarities = cosine_similarity(query_embedding, token_embeddings)

        keywords = [tokens[i].replace("Ġ", "") for i, sim in enumerate(similarities[0]) if sim >= similarity_threshold and tokens[i].isalpha()]
        phrases = []
        for i in range(len(tokens)):
            for window in range(2, window_size + 1):
                if i + window <= len(tokens):
                    phrase = " ".join([tokens[j].replace("Ġ", "") for j in range(i, i + window)])
                    phrase_embedding = token_embeddings[i:i + window].mean(dim=0)
                    phrase_similarity = cosine_similarity(query_embedding, phrase_embedding.unsqueeze(0))[0][0]
                    if phrase_similarity >= similarity_threshold and all(word.isalpha() for word in phrase.split()):
                        phrases.append(phrase)

        return list(set(keywords + phrases))

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
                foreign_keys.setdefault(table_name, []).append({
                    "from": key[3],         # Column in the current table
                    "to_table": key[2],     # Table it references
                    "to_column": key[4]     # Column in the referenced table
                })

        conn.close()
        return foreign_keys
