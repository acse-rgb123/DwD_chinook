import json
import sys
import os
import openai
from modules.pipeline.main_pipeline import Pipeline
import pandas as pd

# Load the OpenAI API key from environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    print("Error: OpenAI API key not set. Please set the OPENAI_API_KEY environment variable.")
    sys.exit(1)

# Disable parallelism warnings for tokenizers
os.environ["TOKENIZERS_PARALLELISM"] = "false"

def main():
    # Load the JSON configuration from the config file
    config_file = "config.json"

    if not os.path.exists(config_file):
        print(f"Error: Configuration file {config_file} not found.")
        sys.exit(1)

    with open(config_file, "r") as f:
        config = json.load(f)

    # Extract parameters from JSON
    db_file = config.get("db_file")
    default_query = config.get("user_query", "No default query available.")
    pdf_path = config.get("pdf_path")

    # Validate essential config values
    if not db_file or not pdf_path:
        print("Error: 'db_file' or 'pdf_path' is missing in the configuration.")
        sys.exit(1)

    # Ask the user for a query or use the default query if no input is provided
    try:
        input_query = input(f"Enter a new query (or press Enter to use the default query):\n'{default_query}'\n").strip()
        if input_query:
            print(f"Using the provided query: '{input_query}'")
        else:
            input_query = default_query
            print(f"Using the default query from config.json: '{input_query}'")
    except EOFError:
        # Handle EOFError for non-interactive environments
        print("No input detected. Using the default query.")
        input_query = default_query
        print(f"Using the default query: '{input_query}'")

    # Check if the database file exists
    if not os.path.exists(db_file):
        print(f"Error: Database file '{db_file}' not found.")
        sys.exit(1)

    # Check if the PDF file exists
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file '{pdf_path}' not found.")
        sys.exit(1)

    # Create an instance of the Pipeline class
    pipeline = Pipeline(db_file, input_query, pdf_path)

    print("Running pipeline...")
    sql_query, results_df, analysis = pipeline.run()

    # Print to the terminal
    print("\nGenerated SQL Query:")
    print(sql_query)

    print("\nSQL Query Results:")
    if results_df:
        df = pd.DataFrame(results_df)
        print(df.to_string(index=False))
    else:
        print("No results returned.")

    print("\nAnalysis:")
    print(analysis)

if __name__ == "__main__":
    main()
