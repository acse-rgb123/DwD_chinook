#!/bin/bash

# Step 1: Create necessary directories
echo "Creating directories..."
mkdir -p app static templates

# Step 2: Create chatbot.py in the 'app' directory
echo "Creating chatbot.py..."
cat <<EOL > app/chatbot.py
from flask import Flask, request, jsonify, render_template
from modules.pipeline.main_pipeline import Pipeline
import os

app = Flask(__name__, static_folder='../static', template_folder='../templates')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_query = data.get("query", "")
    db_file = os.getenv("DB_PATH", "/path/to/your/database.sqlite")
    pdf_path = "/path/to/your/pdf.pdf"

    if not user_query:
        return jsonify({"error": "No query provided"}), 400

    try:
        pipeline = Pipeline(db_file, user_query, pdf_path)
        analysis = pipeline.run()
        return jsonify({
            "sql_query": analysis['generated_sql'],
            "results": analysis['query_results'],
            "interpretation": analysis['analysis']
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
EOL
echo "Created app/chatbot.py"

# Step 3: Create main.js in the 'static' directory
echo "Creating main.js..."
cat <<EOL > static/main.js
document.addEventListener('DOMContentLoaded', function () {
    const sendBtn = document.getElementById('sendBtn');
    const userInput = document.getElementById('userInput');
    const chatMessages = document.getElementById('chat-messages');

    function addUserMessage(message) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', 'user-message');
        messageElement.textContent = message;
        chatMessages.appendChild(messageElement);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function addSQLMessage(sqlQuery) {
        const sqlMessageElement = document.createElement('div');
        sqlMessageElement.classList.add('message', 'bot-message');
        sqlMessageElement.innerHTML = \`<pre><code>\${sqlQuery}</code></pre>\`;
        chatMessages.appendChild(sqlMessageElement);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function addTableMessage(results) {
        const tableMessageElement = document.createElement('div');
        tableMessageElement.classList.add('message', 'bot-message');

        const table = document.createElement('table');
        table.classList.add('table-style');

        if (Array.isArray(results) && results.length > 0) {
            const keys = Object.keys(results[0]);
            const thead = document.createElement('thead');
            const headerRow = document.createElement('tr');
            keys.forEach(key => {
                const th = document.createElement('th');
                th.textContent = key;
                headerRow.appendChild(th);
            });
            thead.appendChild(headerRow);
            table.appendChild(thead);

            const tbody = document.createElement('tbody');
            results.forEach(row => {
                const tr = document.createElement('tr');
                keys.forEach(key => {
                    const td = document.createElement('td');
                    td.textContent = row[key];
                    tr.appendChild(td);
                });
                tbody.appendChild(tr);
            });
            table.appendChild(tbody);
        }

        tableMessageElement.appendChild(table);
        chatMessages.appendChild(tableMessageElement);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function addInterpretationMessage(interpretation) {
        const interpretationElement = document.createElement('div');
        interpretationElement.classList.add('message', 'bot-message');
        interpretationElement.textContent = interpretation;
        chatMessages.appendChild(interpretationElement);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function getBotResponse(userMessage) {
        fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query: userMessage })
        })
        .then(response => response.json())
        .then(data => {
            if (data.sql_query) {
                addSQLMessage(data.sql_query);
            }
            if (data.results && Array.isArray(data.results)) {
                addTableMessage(data.results);
            }
            if (data.interpretation) {
                addInterpretationMessage(data.interpretation);
            }
        })
        .catch(error => {
            console.error("Error:", error);
            addInterpretationMessage("There was an error connecting to the server.");
        });
    }

    sendBtn.addEventListener('click', function () {
        const message = userInput.value;
        if (message.trim() !== "") {
            addUserMessage(message);
            userInput.value = '';
            getBotResponse(message);
        }
    });

    userInput.addEventListener('keydown', function (e) {
        if (e.key === 'Enter') {
            sendBtn.click();
        }
    });
});
EOL
echo "Created static/main.js"

# Step 4: Create style.css in the 'static' directory
echo "Creating style.css..."
cat <<EOL > static/style.css
/* Basic Reset */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    font-family: Arial, sans-serif;
}

body {
    background-color: #e9f5ee;
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
    margin: 0;
}

/* Chat Container */
.chat-container {
    width: 50vw;
    max-width: 800px;
    min-width: 400px;
    height: 85vh;
    max-height: 90vh;
    background-color: #ffffff;
    border-radius: 20px;
    box-shadow: 0px 10px 30px rgba(0, 0, 0, 0.1);
    display: flex;
    flex-direction: column;
    overflow: hidden;
}

/* Chat Header with Wavy Top */
.chat-header {
    position: relative;
    overflow: hidden;
    height: 150px;
    margin-bottom: 20px;
}

.wave-container {
    position: absolute;
    width: 100%;
    height: 100%;
    top: 0;
    left: 0;
    overflow: hidden;
}

.wave {
    position: absolute;
    width: 200%;
    height: 200px;
    background-color: #004225;
    opacity: 0.6;
    top: -100px;
    border-radius: 100%;
    animation: waveAnimation 8s infinite ease-in-out;
}

.wave1 {
    background-color: #004225;
}

.wave2 {
    background-color: #005f35;
    opacity: 0.5;
    animation-delay: -2s;
}

.wave3 {
    background-color: #007a45;
    opacity: 0.4;
    animation-delay: -4s;
}

@keyframes waveAnimation {
    0% {
        transform: translateX(-50%);
    }
    50% {
        transform: translateX(50%);
    }
    100% {
        transform: translateX(-50%);
    }
}

/* Chat Messages */
.chat-messages {
    padding: 1rem;
    flex-grow: 1;
    overflow-y: auto;
    background-color: #f1f9f5;
}

.message {
    background-color: #ffffff;
    padding: 1rem;
    border-radius: 1rem;
    margin-bottom: 1rem;
    max-width: 80%;
    font-size: 1.2rem;
}

.bot-message {
    background-color: #004225;
    color: white;
    margin-right: auto;
    display: inline-block;
    width: 100%;
}

.user-message {
    background-color: #b3e6cd;
    margin-left: auto;
}

/* SQL Query as Code Block */
pre {
    background-color: #2e7d32;
    color: #fff;
    padding: 10px;
    border-radius: 8px;
    white-space: pre-wrap;
    font-size: 1rem;
}

/* Query Results Table Styling */
.table-style {
    width: 100%;
    border-collapse: collapse;
    margin: 10px 0;
    table-layout: auto;
}

.table-style th, .table-style td {
    border: 1px solid #ddd;
    padding: 8px;
    text-align: left;
}

.table-style th {
    background-color: #004225;
    color: white;
}

.table-style tr:nth-child(even) {
    background-color: #b3e6cd;
}

.table-style tr:hover {
    background-color: #ddd;
}

/* Interpretation Text Styling */
.interpretation {
    padding: 1rem;
    background-color: #004225;
    color: white;
    border-radius: 8px;
    margin-bottom: 1rem;
    font-size: 1.2rem;
    white-space: pre-wrap;
}

/* Chat Input */
.chat-input {
    padding: 1rem;
    background-color: #f1f9f5;
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.chat-input input {
    width: 85%;
    padding: 1rem;
    border: 2px solid #004225;
    border-radius: 10px;
    font-size: 1.2rem;
    outline: none;
}

.send-btn {
    background-color: #004225;
    color: white;
    border: none;
    border-radius: 50%;
    padding: 1rem;
    font-size: 1.5rem;
    cursor: pointer;
    animation: wave 2s ease-in-out infinite;
}

.send-btn:hover {
    background-color: #002810;
}

/* Mini waves and bubble animations */
@keyframes wave {
    0% {
        transform: translateY(0);
    }
    50% {
        transform: translateY(-10px);
    }
    100% {
        transform: translateY(0);
    }
}

@keyframes bubble {
    0% {
        opacity: 0;
        transform: scale(0.8);
    }
    100% {
        opacity: 1;
        transform: scale(1);
    }
}

.message {
    animation: bubble 0.3s ease-out;
}

/* Responsive Design */
@media (max-width: 1024px) {
    .chat-container {
        width: 70vw;
        height: 80vh;
    }
}

@media (max-width: 768px) {
    .chat-container {
        width: 90vw;
        height: 80vh;
    }

    .chat-header {
        height: 100px;
    }

    .wave {
        height: 150px;
        top: -75px;
    }
}
EOL
echo "Created static/style.css"

# Step 5: Create index.html in the 'templates' directory
echo "Creating index.html..."
cat <<EOL > templates/index.html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chatbot Interface</title>
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>
    <div class="chat-container">
        <div id="chat-messages" class="chat-messages"></div>
        <div class="chat-input">
            <input type="text" id="userInput" placeholder="Type your query here...">
            <button id="sendBtn" class="send-btn">></button>
        </div>
    </div>
    <script src="/static/main.js"></script>
</body>
</html>
EOL
echo "Created templates/index.html"

echo "All files have been created successfully."
