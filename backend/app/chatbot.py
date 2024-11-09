from flask import Flask, request, jsonify, render_template
import json
import os
import pandas as pd
from modules.pipeline.main_pipeline import Pipeline

app = Flask(__name__, static_folder='../../frontend/static', template_folder='../../frontend/templates')

# Load configuration from config.json
config_file_path = os.path.join(os.path.dirname(__file__), '../config.json')
if os.path.exists(config_file_path):
    with open(config_file_path, 'r') as config_file:
        config = json.load(config_file)
        db_file = config.get("db_file", "")
        default_user_query = config.get("user_query", "")
        pdf_path = config.get("pdf_path", "")
else:
    print(f"Error: config.json not found at {config_file_path}. Ensure it exists.")
    db_file = ""
    pdf_path = ""
    default_user_query = ""  # Ensure this is initialized

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_query = data.get("query", default_user_query)  # Use provided query or default from config

    if not user_query:
        return jsonify({"error": "No query provided"}), 400

    if not os.path.exists(db_file):
        return jsonify({"error": f"Database file not found at {db_file}"}), 400

    if not os.path.exists(pdf_path):
        return jsonify({"error": f"PDF file not found at {pdf_path}"}), 400

    try:
        pipeline = Pipeline(db_file, user_query, pdf_path)
        sql_query, results_df, analysis = pipeline.run()

        # Return as JSON to the frontend
        return jsonify({
            "sql_query": sql_query,
            "results": results_df,
            "analysis": analysis
        })
    except Exception as e:
        print(f"Server error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
