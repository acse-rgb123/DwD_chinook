import networkx as nx

class SubschemaCreator:
    def __init__(self, schema, foreign_keys):
        self.schema = schema
        self.foreign_keys = foreign_keys

    def get_associated_tables(self, mapped_columns):
        associated_tables = set()
        for keyword, column_matches in mapped_columns.items():
            for column, _ in column_matches:
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
        
        # Debug: Print table connections
        for conn in connections:
            print(f"    {conn[0]} <-> {conn[1]} (From: {conn[2]['from_column']}, To: {conn[2]['to_column']})")

        return connections

    def create_optimized_subschema(self, relevant_tables):
        subschema_graph = nx.Graph()

        # Add relevant tables as nodes
        for table in relevant_tables:
            if table in self.schema:
                subschema_graph.add_node(table)
                print(f"Added Node: {table}")

        # Add relationships for relevant tables
        for table in relevant_tables:
            if table in self.foreign_keys:
                for relation in self.foreign_keys[table]:
                    if relation['to_table'] in relevant_tables:
                        subschema_graph.add_edge(table, relation['to_table'], from_column=relation['from'], to_column=relation['to_column'])
                        print(f"Added Edge: {table} -> {relation['to_table']} (From: {relation['from']}, To: {relation['to_column']})")

        # Print edges after adding relationships
        print(f"Subschema Edges: {list(subschema_graph.edges(data=True))}")

        return subschema_graph

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
        
        # Debug: Print Join Paths
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
