import os
import spacy
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from tabulate import tabulate
import pandas as pd

class TableRAG:
    def __init__(self, embedding_handler, documentation, schema):
        self.embedding_handler = embedding_handler
        self.documentation = documentation
        self.schema = schema  # Store schema information
        self.nlp = spacy.load("en_core_web_sm")  # Load spaCy model for NER
        self.doc_chunks, self.chunk_embeddings = self.process_and_embed_documentation()

    def process_and_embed_documentation(self):
        doc_chunks = {}
        chunk_embeddings = {}

        print("Flattening and chunking documentation sections...")
        
        for doc_key, doc_text in self.documentation.items():
            if not doc_text.strip():
                print(f"Warning: Empty document text for section '{doc_key}'. Skipping.")
                continue

            sections = self.chunk_document(doc_text, max_chunk_size=100)
            for i, section in enumerate(sections):
                chunk_key = f"{doc_key}_chunk_{i}"
                doc_chunks[chunk_key] = section
                chunk_embeddings[chunk_key] = self.embedding_handler.get_embedding(section)
            
        print("Completed embedding documentation chunks.")
        return doc_chunks, chunk_embeddings

    def chunk_document(self, text, max_chunk_size=100):
        words = text.split()
        chunks = [" ".join(words[i:i + max_chunk_size]) for i in range(0, len(words), max_chunk_size)]
        return chunks

    def extract_entities(self, text):
        """Extract entities from text using spaCy NER."""
        doc = self.nlp(text)
        entities = [(ent.text, ent.label_) for ent in doc.ents]
        return entities

    def find_relevant_tables(self, user_query):
        """
        Identify tables relevant to the user query by leveraging 
        entities and contextual information from the documentation.
        """
        # Extract entities from the query
        query_entities = self.extract_entities(user_query)
        print(f"Entities in User Query: {query_entities}")

        # Cross-reference entities with documentation to find related tables
        relevant_tables = set()
        for keyword, label in query_entities:
            for doc_key, doc_text in self.documentation.items():
                doc_entities = self.extract_entities(doc_text)
                for doc_entity_text, doc_entity_label in doc_entities:
                    if doc_entity_label == label:
                        related_table = self.find_related_table_from_entity(doc_entity_text)
                        if related_table:
                            relevant_tables.add(related_table)
        
        print(f"Relevant Tables Identified: {relevant_tables}")
        return list(relevant_tables)

    def find_related_table_from_entity(self, entity_text):
        """
        Use schema embeddings to find a table related to the entity text.
        """
        entity_embedding = self.embedding_handler.get_embedding(entity_text)
        max_similarity = 0
        best_match_table = None

        # Compare entity embedding with each table's embedding in the schema
        for table in self.schema.keys():
            table_embedding = self.embedding_handler.get_embedding(table)
            similarity = cosine_similarity([entity_embedding], [table_embedding])[0][0]
            
            if similarity > max_similarity:
                max_similarity = similarity
                best_match_table = table

        if max_similarity > 0.5:  # Only return if similarity threshold is met
            print(f"Entity '{entity_text}' matched with table '{best_match_table}' (Similarity: {max_similarity})")
            return best_match_table
        return None
