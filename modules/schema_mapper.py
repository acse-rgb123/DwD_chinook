import pandas as pd

class SchemaMapper:
    def __init__(self, schema, foreign_keys, embedding_handler):
        self.schema = schema
        self.foreign_keys = foreign_keys  # Add this to initialize foreign_keys
        self.embedding_handler = embedding_handler

    def identify_relevant_tables(self, keywords, similarity_threshold=0.75):
        relevant_tables = set()
        keyword_embeddings = self.embedding_handler.get_embeddings_batch(keywords)  # Get embeddings for keywords

        for keyword, keyword_embedding in zip(keywords, keyword_embeddings):
            for table in self.schema.keys():
                table_embedding = self.embedding_handler.get_embedding(table)  # Get embedding for table name
                if self.embedding_handler.calculate_similarity(keyword_embedding, table_embedding) >= similarity_threshold:
                    relevant_tables.add(table)

        # Debug: Print relevant tables
        print(f"Relevant Tables: {relevant_tables}")

        return list(relevant_tables)

    def map_keywords_to_columns(self, keywords, relevant_tables, similarity_threshold=0.60):
        mapped_columns = {}
        similarity_scores = []  # To store similarity scores for display
        keyword_embeddings = self.embedding_handler.get_embeddings_batch(keywords)

        for keyword, keyword_embedding in zip(keywords, keyword_embeddings):
            best_matches = []
            for table in relevant_tables:
                columns = self.schema[table]
                column_descriptions = columns  # Directly use column names
                column_embeddings = self.embedding_handler.get_embeddings_batch(column_descriptions)

                for column_description, column_embedding in zip(column_descriptions, column_embeddings):
                    similarity = self.embedding_handler.calculate_similarity(keyword_embedding, column_embedding)
                    if similarity >= similarity_threshold:
                        best_matches.append((column_description, similarity))
                        # Store the similarity score for display
                        similarity_scores.append((keyword, column_description, similarity))

            # Sort matches by similarity and keep the top 3
            best_matches = sorted(best_matches, key=lambda x: x[1], reverse=True)[:3]
            mapped_columns[keyword] = best_matches

        # Create a DataFrame from similarity scores for debugging or analysis
        similarity_df = pd.DataFrame(similarity_scores, columns=['Keyword', 'Column', 'Similarity'])
        similarity_df = similarity_df.sort_values(by='Similarity', ascending=False)

        # Print the top 10 and bottom 10 similarity scores for debugging
        print("\nTop 10 Similarity Scores between Keywords and Columns:")
        print(similarity_df.head(10))

        print("\nBottom 10 Similarity Scores between Keywords and Columns:")
        print(similarity_df.tail(10))

        # Return only the mapped columns (no subgraph, no extra info)
        return mapped_columns

