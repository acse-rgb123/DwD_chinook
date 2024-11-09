import pandas as pd
from ..subschema.schema_mapper import SchemaMapper
from ..subschema.schema_extractor import SchemaExtractor
from ..subschema.subschema import SubschemaCreator
from ..other.keyword_extractor import KeywordExtractor


class SubschemaPipeline:
    def __init__(self, db_file, embedding_handler, method="roberta"):
        self.embedding_handler = embedding_handler
        self.schema_extractor = SchemaExtractor(db_file, self.embedding_handler)
        self.keyword_extractor = KeywordExtractor(method)
        self.schema = self.schema_extractor.extract_schema_from_db()
        self.foreign_keys = self.schema_extractor.extract_foreign_key_relations()
        self.schema_mapper = SchemaMapper(
            self.schema, self.foreign_keys, self.embedding_handler
        )
        self.subschema_creator = SubschemaCreator(self.schema, self.foreign_keys)

    def extract_keywords(self, user_query):
        """Extract keywords using the specified method in KeywordExtractor."""
        print("Extracting keywords...")
        keywords = self.keyword_extractor.extract_keywords(
            user_query
        )  # Correct method call
        print(f"Extracted Keywords:\n{pd.Series(keywords)}")
        return keywords

    def identify_relevant_tables(self, keywords, similarity_threshold=0.30):
        """Identify relevant tables based on keywords."""
        print("Identifying relevant tables...")
        relevant_tables = self.schema_mapper.identify_relevant_tables(
            keywords, similarity_threshold
        )
        print(f"Relevant Tables: {relevant_tables}")
        return relevant_tables

    def create_joins(self, relevant_tables):
        """Create joins between relevant tables based on primary and foreign keys."""
        print("Creating joins between relevant tables...")
        joins = self.subschema_creator.find_table_connections(relevant_tables)
        formatted_joins = []
        for join in joins:
            formatted_joins.append(
                {
                    "tables": (join[0], join[1]),
                    "columns": (join[2]["from_column"], join[2]["to_column"]),
                }
            )
            print(
                f"{join[0]} <-> {join[1]} (From: {join[2]['from_column']}, To: {join[2]['to_column']})"
            )
        return formatted_joins
