import openai
import os

class LLM:
    def __init__(self):
        pass

    def generate_sql_with_rag(self, user_query, relevant_columns, joins, column_documentation_matches, relevant_docs):
        context = ""
        for column, matches in column_documentation_matches.items():
            context += f"Documentation for {column}:\n"
            for match in matches:
                context += f"- {match[0]}\n"
        rag_context = "Retrieved Documentation Context:\n" + "\n".join(relevant_docs)
        join_conditions = []
        for join_path in joins:
            for join in join_path:
                table1, table2 = join['tables']
                from_column, to_column = join['columns']
                join_conditions.append(f"{table1}.{from_column} = {table2}.{to_column}")
        input_text = f"""
        User Question: {user_query}
        ONLY USE THESE columns: {', '.join(relevant_columns)}
        ONLY USE join conditions: {', '.join(join_conditions)}
        Generate only the correct SQLlite query to answer this query please. no additional comments.
        Include all information neccessary in the SQL select labelled appropriatley to answer {user_query};
        """
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a maste at generating SQL queries based on user inputs and database schema."},
                {"role": "user", "content": input_text}
            ],
            max_tokens=300,
            temperature=0.2
        )
        return response['choices'][0]['message']['content'].strip()

    def analyze_result(self, user_query, result_df):
        input_text = f"""
        Answer the User Question: {user_query}
        Using the following results table: {result_df}
        Provide a concise answer.
        """
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You analyze result tables and provide concise numerical or summarized answers."},
                {"role": "user", "content": input_text}
            ],
            max_tokens=150,
            temperature=0.2
        )
        return response['choices'][0]['message']['content'].strip()
