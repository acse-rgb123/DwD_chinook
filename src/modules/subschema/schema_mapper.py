import pandas as pd
from tabulate import tabulate

import pandas as pd
from tabulate import tabulate

class SchemaMapper:
    def __init__(self, schema, foreign_keys, embedding_handler):
        self.schema = schema
        self.foreign_keys = foreign_keys  # Initialize foreign keys
        self.embedding_handler = embedding_handler

    def identify_relevant_tables_and_columns(self, keywords, similarity_threshold=0.55):
        relevant_tables = []  # Changed from set to list to allow appending in the main pipeline
        relevant_columns = []  # List to store relevant columns and their similarity scores
        keyword_embeddings = self.embedding_handler.get_embeddings_batch(keywords)  # Get embeddings for keywords

        # Create a list to store the results in a structured way
        results = []

        for keyword, keyword_embedding in zip(keywords, keyword_embeddings):
            # Loop through each table in the schema
            for table, columns in self.schema.items():
                table_embedding = self.embedding_handler.get_embedding(table)  # Get embedding for table name

                # Check if the table itself is relevant based on the similarity threshold
                table_similarity = self.embedding_handler.calculate_similarity(keyword_embedding, table_embedding)
                if table_similarity >= similarity_threshold:
                    if table not in relevant_tables:  # Avoid duplicates
                        relevant_tables.append(table)

                    # Now check columns within the table by combining table and column names
                    for column in columns:
                        table_column = f"{table}.{column}"  # Combine table and column names
                        column_embedding = self.embedding_handler.get_embedding(table_column)  # Get embedding for table.column

                        # Calculate the similarity for the combined table.column
                        column_similarity = self.embedding_handler.calculate_similarity(keyword_embedding, column_embedding)

                        # If the similarity for the combined table.column exceeds the threshold, add it to relevant columns
                        if column_similarity >= similarity_threshold:
                            relevant_columns.append((table, column, column_similarity))
                            results.append({
                                "Keyword": keyword,
                                "Table.Column": table_column,
                                "Similarity Score": column_similarity
                            })

        # Convert the results into a DataFrame for neat printing
        df_results = pd.DataFrame(results)

        # Print the relevant tables and columns in a table format
        print("\nRelevant Tables and Columns with Similarity Scores:")
        print(tabulate(df_results, headers='keys', tablefmt='pretty'))

        # Return relevant tables as a list and relevant columns along with their similarity scores
        return relevant_tables, relevant_columns  # Return as list


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

        # Create a DataFrame from similarity scores for analysis
        similarity_df = pd.DataFrame(similarity_scores, columns=['Keyword', 'Column', 'Similarity'])
        similarity_df = similarity_df.sort_values(by='Similarity', ascending=False)

        # Print the top 10 similarity scores for debugging
        print("\nTop 10 Similarity Scores between Keywords and Columns:")
        print(tabulate(similarity_df.head(10), headers='keys', tablefmt='pretty'))

        # Print the bottom 10 similarity scores for debugging
        print("\nBottom 10 Similarity Scores between Keywords and Columns:")
        print(tabulate(similarity_df.tail(10), headers='keys', tablefmt='pretty'))

        # Return only the mapped columns
        return mapped_columns

