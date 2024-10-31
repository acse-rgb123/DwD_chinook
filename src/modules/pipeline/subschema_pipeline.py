import pandas as pd
from ..subschema.schema_mapper import SchemaMapper
from ..subschema.schema_extractor import SchemaExtractor
from ..subschema.subschema import SubschemaCreator

class SubschemaPipeline:
    def __init__(self, db_file, embedding_handler):
        self.embedding_handler = embedding_handler
        self.schema_extractor = SchemaExtractor(db_file, self.embedding_handler)
        self.subschema_creator = SubschemaCreator(
            self.schema_extractor.extract_schema_from_db(),
            self.schema_extractor.extract_foreign_key_relations()
        )

    def extract_schema_and_foreign_keys(self):
        print("Extracting schema and foreign key relationships...")
        schema = self.schema_extractor.extract_schema_from_db()
        foreign_keys = self.schema_extractor.extract_foreign_key_relations()
        return schema, foreign_keys

    def extract_keywords(self, user_query):
        print("Extracting keywords using RoBERTa...")
        keywords = self.schema_extractor.extract_keywords_with_roberta(user_query)
        print(f"Extracted Keywords:\n{pd.Series(keywords)}")
        return keywords

    def map_keywords_to_schema(self, schema, foreign_keys, keywords):
        print("Mapping keywords to schema...")
        schema_mapper = SchemaMapper(schema, foreign_keys, self.embedding_handler)
        relevant_tables, relevant_columns = schema_mapper.identify_relevant_tables_and_columns(keywords)

        mapped_columns = schema_mapper.map_keywords_to_columns(keywords, relevant_tables)

        print("\nTable Connections:")
        for connection in self.subschema_creator.find_table_connections(relevant_tables):
            print(f"{connection[0]} <-> {connection[1]} (From: {connection[2]['from_column']}, To: {connection[2]['to_column']})")

        subgraph = self.subschema_creator.create_optimized_subschema(relevant_tables)
        print("\nSubschema Nodes:")
        print(subgraph.nodes())

        print("\nSubschema Edges (Foreign Key Joins with Column Info):")
        for edge in subgraph.edges(data=True):
            print(f"{edge[0]} <-> {edge[1]} (From: {edge[2]['from_column']}, To: {edge[2]['to_column']})")

        join_paths = self.subschema_creator.find_paths_between_tables(subgraph, start_table="Customer")
        if not join_paths:
            print("\nAdding necessary tables for join paths.")
            subgraph.add_node('Customer')
            join_paths = self.subschema_creator.find_paths_between_tables(subgraph, start_table="Customer")

        print("\nJoin Paths:")
        for path in join_paths:
            for join in path:
                print(f"{join['tables'][0]} -> {join['tables'][1]} (From: {join['columns'][0]}, To: {join['columns'][1]})")

        return mapped_columns, join_paths
