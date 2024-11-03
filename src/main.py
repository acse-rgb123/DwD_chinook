import json
import sys
import os
import openai
from modules.pipeline.main_pipeline import Pipeline

openai.api_key = 'sk-_ynWP8bFt1E-Lg6ZxIAt8YV1fdB8qU1SMkWCqMVRtmT3BlbkFJ_FWv5x5Oz1lT6vhGwUtODMSKo36FCBHBW30fYvD3sA'
os.environ["TOKENIZERS_PARALLELISM"] = "false"

def main():
    # Load the JSON configuration from a hardcoded config file
    config_file = "config.json"

    # Load the JSON configuration
    if not os.path.exists(config_file):
        print(f"Error: Configuration file {config_file} not found.")
        sys.exit(1)

    with open(config_file, 'r') as f:
        config = json.load(f)

    # Extract parameters from JSON
    db_file = config['db_file']
    user_query = config['user_query']
    pdf_path = config['pdf_path']

    # Ask the user for a query, or use the one from config.json if no input is provided
    input_query = input(f"Enter a new query (or press Enter to use the default query from config.json):\n'{user_query}'\n")
    
    if input_query.strip():
        user_query = input_query
        print(f"Using the provided query: {user_query}")
    else:
        print(f"Using the default query from config.json: {user_query}")

    # Check if the database file exists
    if not os.path.exists(db_file):
        print(f"Error: Database file {db_file} not found.")
        sys.exit(1)
    
    # Check if the PDF file exists
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file {pdf_path} not found.")
        sys.exit(1)

    # Create an instance of the Pipeline class
    pipeline = Pipeline(db_file, user_query, pdf_path)

    # Run the pipeline and get the analysis result
    analysis = pipeline.run()
    print("Analysis of SQL results:", analysis)

if __name__ == "__main__":
    main()
