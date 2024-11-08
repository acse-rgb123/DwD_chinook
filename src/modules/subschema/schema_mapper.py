import pandas as pd
from tabulate import tabulate


class SchemaMapper:
    def __init__(self, schema, foreign_keys, embedding_handler):
        self.schema = schema
        self.foreign_keys = foreign_keys
        self.embedding_handler = embedding_handler

    def identify_relevant_tables(self, keywords, similarity_threshold=0.45):
        relevant_tables = set()
        keyword_embeddings = self.embedding_handler.get_embeddings_batch(keywords)
        results = []

        for keyword, keyword_embedding in zip(keywords, keyword_embeddings):
            for table in self.schema.keys():
                table_embedding = self.embedding_handler.get_embedding(table)
                table_similarity = self.embedding_handler.calculate_similarity(
                    keyword_embedding, table_embedding
                )

                if table_similarity >= similarity_threshold:
                    relevant_tables.add(table)
                    results.append(
                        {
                            "Keyword": keyword,
                            "Table": table,
                            "Similarity Score": table_similarity,
                        }
                    )

        # Convert results to DataFrame for printing
        df_results = pd.DataFrame(results)
        print("\nRelevant Tables with Similarity Scores:")
        print(tabulate(df_results, headers="keys", tablefmt="pretty"))

        return list(relevant_tables)

    def map_keywords_to_columns(
        self, keywords, relevant_tables, similarity_threshold=0.40
    ):
        mapped_columns = {}
        similarity_scores = []
        keyword_embeddings = self.embedding_handler.get_embeddings_batch(keywords)

        for keyword, keyword_embedding in zip(keywords, keyword_embeddings):
            best_matches = []
            for table in relevant_tables:
                columns = self.schema[table]
                column_embeddings = self.embedding_handler.get_embeddings_batch(columns)

                for column, column_embedding in zip(columns, column_embeddings):
                    similarity = self.embedding_handler.calculate_similarity(
                        keyword_embedding, column_embedding
                    )

                    if similarity >= similarity_threshold:
                        table_column = f"{table}.{column}"
                        best_matches.append((table_column, similarity))
                        similarity_scores.append((keyword, table_column, similarity))

            best_matches = sorted(best_matches, key=lambda x: x[1], reverse=True)[:3]
            mapped_columns[keyword] = best_matches

        # Display similarity scores for debugging
        similarity_df = pd.DataFrame(
            similarity_scores, columns=["Keyword", "Table.Column", "Similarity"]
        )
        similarity_df = similarity_df.sort_values(by="Similarity", ascending=False)
        print("\nTop Similarity Scores between Keywords and Columns:")
        print(tabulate(similarity_df.head(10), headers="keys", tablefmt="pretty"))

        return mapped_columns
