import os
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from tabulate import tabulate
import pandas as pd
from ..other.keyword_extractor import KeywordExtractor


class TableRAG:
    def __init__(
        self,
        embedding_handler,
        documentation,
        schema,
        keyword_extraction_method="roberta",
    ):
        self.embedding_handler = embedding_handler
        self.documentation = documentation
        self.schema = schema  # Store schema information
        self.keyword_extractor = KeywordExtractor(method=keyword_extraction_method)
        self.doc_chunks, self.chunk_embeddings = self.process_and_embed_documentation()

    def process_and_embed_documentation(self):
        doc_chunks = {}
        chunk_embeddings = {}

        print("Flattening and chunking documentation sections...")

        for doc_key, doc_text in self.documentation.items():
            if not doc_text.strip():
                print(
                    f"Warning: Empty document text for section '{doc_key}'. Skipping."
                )
                continue

            sections = self.chunk_document(doc_text, max_chunk_size=100)
            for i, section in enumerate(sections):
                chunk_key = f"{doc_key}_chunk_{i}"
                doc_chunks[chunk_key] = section
                chunk_embeddings[chunk_key] = self.embedding_handler.get_embedding(
                    section
                )

        print("Completed embedding documentation chunks.")
        return doc_chunks, chunk_embeddings

    def chunk_document(self, text, max_chunk_size=300):
        words = text.split()
        chunks = [
            " ".join(words[i : i + max_chunk_size])
            for i in range(0, len(words), max_chunk_size)
        ]
        return chunks

    def find_relevant_tables(self, user_query):
        """
        Identify tables relevant to the user query by leveraging
        keywords and contextual information from the documentation.
        """
        # Extract keywords using KeywordExtractor
        query_keywords = self.keyword_extractor.extract_keywords(user_query)
        print(f"Keywords in User Query: {query_keywords}")

        # Cross-reference keywords with documentation to find related tables
        relevant_tables = set()
        for keyword in query_keywords:
            for doc_key, doc_text in self.documentation.items():
                doc_keywords = self.keyword_extractor.extract_keywords(doc_text)
                if keyword in doc_keywords:
                    related_table = self.find_related_table_from_keyword(keyword)
                    if related_table:
                        relevant_tables.add(related_table)

        print(f"Relevant Tables Identified: {relevant_tables}")
        return list(relevant_tables)

    def find_related_table_from_keyword(self, keyword):
        """
        Use schema embeddings to find a table related to the keyword.
        """
        keyword_embedding = self.embedding_handler.get_embedding(keyword)
        max_similarity = 0
        best_match_table = None

        # Compare keyword embedding with each table's embedding in the schema
        for table in self.schema.keys():
            table_embedding = self.embedding_handler.get_embedding(table)
            similarity = cosine_similarity([keyword_embedding], [table_embedding])[0][0]

            if similarity > max_similarity:
                max_similarity = similarity
                best_match_table = table

        if max_similarity > 0.30:  # Only return if similarity threshold is met
            print(
                f"Keyword '{keyword}' matched with table '{best_match_table}' (Similarity: {max_similarity})"
            )
            return best_match_table
        return None
