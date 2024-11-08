import openai
import os


class LLM:
    def __init__(self):
        pass

    def generate_sql_with_rag(self, user_query, joins, relevant_docs):
        # Build the documentation context from `relevant_docs`
        context = "\n".join(relevant_docs)

        # Format the join conditions from the `joins` structure
        join_conditions = []
        selected_tables = set()
        for join in joins:
            table1, table2 = join["tables"]
            from_column, to_column = join["columns"]
            join_conditions.append(f"{table1}.{from_column} = {table2}.{to_column}")
            selected_tables.update([table1, table2])

        # Construct the input text for the LLM with subschema information and user query
        input_text = f"""
        User Query: {user_query}
        Documentation Context: {context}
        
        SUBSCHEMA TABLES: {selected_tables}
        SUBSCHEMA JOINS: {join_conditions}
        
        Generate only the correct SQLite query with correct table names to answer this query. 
        Please label appropriately and include all necessary information.
        """

        print("Input Text to LLM:")
        print(input_text)

        # Send request to OpenAI to generate the SQL
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are a master at generating SQL queries based on user inputs and database schema.",
                },
                {"role": "user", "content": input_text},
            ],
            max_tokens=300,
            temperature=0.2,
        )
        return response["choices"][0]["message"]["content"].strip()

    def analyze_result(self, user_query, sql_query, result_df):
        # Prepare the input with the SQL query and the result DataFrame for analysis
        input_text = f"""
        User Question: {user_query}
        SQL Query Used: {sql_query}
        SQL Query Result: {result_df}
        Provide a concise answer based on the query and result.
        """

        # Send the query, SQL, and result to the LLM for analysis
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You analyze SQL queries and their results to provide accurate answers to user questions.",
                },
                {"role": "user", "content": input_text},
            ],
            max_tokens=200,
            temperature=0.2,
        )
        return response["choices"][0]["message"]["content"].strip()
