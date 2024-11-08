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
        sqlMessageElement.innerHTML = `<pre><code>${sqlQuery}</code></pre>`;
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
            if (data.analysis) {
                addInterpretationMessage(data.analysis);
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
