import networkx as nx
import pandas as pd

class SchemaMapper:
    def __init__(self, schema, foreign_keys, embedding_handler):
        self.schema = schema
        self.foreign_keys = foreign_keys
        self.embedding_handler = embedding_handler

    def identify_relevant_tables(self, keywords, similarity_threshold=0.75):
        relevant_tables = set()
        keyword_embeddings = self.embedding_handler.get_embeddings_batch(keywords)  # Get embeddings for keywords

        for keyword, keyword_embedding in zip(keywords, keyword_embeddings):
            for table in self.schema.keys():
                table_embedding = self.embedding_handler.get_embedding(table)  # Get embedding for table name
                if self.embedding_handler.calculate_similarity(keyword_embedding, table_embedding) >= similarity_threshold:
                    relevant_tables.add(table)

        return list(relevant_tables)

    def map_keywords_to_columns(self, keywords, relevant_tables, similarity_threshold=0.70):
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

        # Create a DataFrame from similarity scores
        similarity_df = pd.DataFrame(similarity_scores, columns=['Keyword', 'Column', 'Similarity'])
        
        # Sort the DataFrame by Similarity
        similarity_df = similarity_df.sort_values(by='Similarity', ascending=False)

        # Print the top 10 and bottom 10 similarity scores
        print("\nTop 10 Similarity Scores between Keywords and Columns:")
        print(similarity_df.head(10))

        print("\nBottom 10 Similarity Scores between Keywords and Columns:")
        print(similarity_df.tail(10))

        return mapped_columns  # Return the mapped_columns


    def get_associated_tables(self, mapped_columns):
        associated_tables = set()
        for keyword, column_matches in mapped_columns.items():
            for column, _ in column_matches:
                # Here, we can get the table from the schema directly
                for table, columns in self.schema.items():
                    if column in columns:
                        associated_tables.add(table)

        print("\nAssociated Tables:")
        for table in associated_tables:
            print(f"    {table}")

        return list(associated_tables)

    def find_table_connections(self, associated_tables):
        connections = []
        for table in associated_tables:
            if table in self.foreign_keys:
                for relation in self.foreign_keys[table]:
                    if relation['to_table'] in associated_tables:
                        connections.append((table, relation['to_table'], {
                            'from_column': relation['from'], 'to_column': relation['to_column']
                        }))
        
        print("\nTable Connections:")
        for conn in connections:
            print(f"    {conn[0]} <-> {conn[1]} (From: {conn[2]['from_column']}, To: {conn[2]['to_column']})")

        return connections

    def create_optimized_subschema(self, relevant_tables):
        subschema_graph = nx.Graph()

        # Start by adding relevant tables to the graph
        for table in relevant_tables:
            if table in self.schema:
                subschema_graph.add_node(table)

        # Add relationships for relevant tables
        for table in relevant_tables:
            if table in self.foreign_keys:
                for relation in self.foreign_keys[table]:
                    if relation['to_table'] in relevant_tables:
                        subschema_graph.add_edge(table, relation['to_table'], 
                                                from_column=relation['from'], 
                                                to_column=relation['to_column'])

        # Dynamically include any necessary tables based on foreign key relationships
        necessary_tables = set()  # Use a set to avoid duplicates

        for table in relevant_tables:
            if table in self.foreign_keys:
                for relation in self.foreign_keys[table]:
                    necessary_tables.add(relation['to_table'])  # Add related tables

        # Add necessary tables to the graph if they are not already included
        for necessary_table in necessary_tables:
            if necessary_table in self.schema and necessary_table not in subschema_graph.nodes:
                subschema_graph.add_node(necessary_table)

        # Construct edges again to include newly added necessary tables
        for table in relevant_tables:
            if table in self.foreign_keys:
                for relation in self.foreign_keys[table]:
                    if relation['to_table'] in necessary_tables:
                        subschema_graph.add_edge(table, relation['to_table'], 
                                                from_column=relation['from'], 
                                                to_column=relation['to_column'])

        # Create the minimum spanning tree from the constructed graph
        mst = nx.minimum_spanning_tree(subschema_graph)

        # Debug: Print subschema nodes and edges
        print("\nSubschema Nodes:")
        print(f"    {list(mst.nodes())}")
        print("Subschema Edges (Foreign Key Joins with Column Info):")
        for edge in mst.edges(data=True):
            print(f"    {edge[0]} <-> {edge[1]} (From: {edge[2]['from_column']}, To: {edge[2]['to_column']})")

        return mst

    def find_paths_between_tables(self, subgraph, start_table):
        paths = []
        for target_table in subgraph.nodes:
            if target_table != start_table:
                try:
                    path = nx.shortest_path(subgraph, source=start_table, target=target_table)
                    path_with_columns = []
                    for i in range(len(path) - 1):
                        table1 = path[i]
                        table2 = path[i + 1]
                        edge_data = subgraph.get_edge_data(table1, table2)
                        path_with_columns.append({
                            'tables': (table1, table2),
                            'columns': (edge_data['from_column'], edge_data['to_column'])
                        })
                    paths.append(path_with_columns)
                except nx.NetworkXNoPath:
                    continue
        
        # Print Join Paths
        print("\nJoin Paths:")
        for path in paths:
            for step in path:
                print(f"    {step['tables'][0]} -> {step['tables'][1]} (From: {step['columns'][0]}, To: {step['columns'][1]})")

        return paths

    def validate_subschema(self, mapped_columns, table_connections):
        valid_columns = []
        invalid_columns = []

        for keyword, columns in mapped_columns.items():
            for column, _ in columns:
                table = None
                # Find the table for the column
                for tbl, cols in self.schema.items():
                    if column in cols:
                        table = tbl
                        break
                
                if table and column in self.schema[table]:
                    valid_columns.append(f"{table}.{column}")
                else:
                    invalid_columns.append(column)
                    print(f"Invalid column: {column} does not exist in the schema.")

        if invalid_columns:
            raise ValueError(f"Validation failed. Invalid columns: {invalid_columns}")

        if not table_connections:
            raise ValueError("No valid foreign key connections found between tables.")

        return valid_columns, table_connections

    def map_and_generate_subschema(self, keywords, start_table):
        relevant_tables = self.identify_relevant_tables(keywords)
        mapped_columns = self.map_keywords_to_columns(keywords, relevant_tables)
        associated_tables = self.get_associated_tables(mapped_columns)
        table_connections = self.find_table_connections(associated_tables)
        valid_columns, valid_connections = self.validate_subschema(mapped_columns, table_connections)

        subschema_graph = self.create_optimized_subschema(associated_tables)
        print("\nOptimized Subschema Graph Nodes:")
        print(f"    {list(subschema_graph.nodes())}")
        print("Optimized Subschema Graph Edges:")
        for edge in subschema_graph.edges(data=True):
            print(f"    {edge[0]} <-> {edge[1]} (From: {edge[2]['from_column']}, To: {edge[2]['to_column']})")

        join_paths = self.find_paths_between_tables(subschema_graph, start_table="Customer")  
        return subschema_graph, join_paths, valid_columns
