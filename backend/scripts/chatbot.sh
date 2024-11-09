#!/bin/bash

# Step 0: Check if Python is installed and at least version 3.6
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
REQUIRED_VERSION="3.6"
if [[ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]]; then
    echo "Error: Python 3.6 or higher is required."
    exit 1
fi

# Step 1: Check if the virtual environment exists
if [ ! -d "backend/env" ]; then
    echo "Virtual environment not found. Creating a virtual environment..."
    python3 -m venv backend/env

    if [ $? -ne 0 ]; then
        echo "Error: Failed to create virtual environment."
        exit 1
    fi

    # Step 2: Activate the virtual environment
    source backend/env/bin/activate

    # Step 3: Install dependencies
    echo "Installing dependencies..."
    pip install --upgrade pip > /dev/null 2>&1
    pip install \
        pandas \
        networkx \
        openai \
        python-dotenv \
        tabulate \
        PyPDF2 \
        scikit-learn \
        spacy \
        faiss-cpu \
        torch \
        transformers \
        Flask-SSE \
        Flask \
        flask > /dev/null 2>&1  

    if [ $? -ne 0 ]; then
        echo "Error installing dependencies."
        exit 1
    else
        echo "Dependencies installed successfully."
    fi

    # Step 4: Download the spaCy language model
    echo "Downloading spaCy language model..."
    python -m spacy download en_core_web_sm > /dev/null 2>&1

    if [ $? -ne 0 ]; then
        echo "Error downloading spaCy language model."
        exit 1
    else
        echo "spaCy language model downloaded successfully."
    fi
else
    echo "Virtual environment already exists. Activating it..."
    source backend/env/bin/activate

    # Ensure Flask is installed in the existing virtual environment
    if ! python -c "import flask" &> /dev/null; then
        echo "Flask not found in the virtual environment. Installing Flask..."
        pip install flask > /dev/null 2>&1

        if [ $? -ne 0 ]; then
            echo "Error installing Flask."
            exit 1
        else
            echo "Flask installed successfully."
        fi
    fi
fi

# Add 'src' directory to PYTHONPATH
export PYTHONPATH="$PYTHONPATH:$(pwd)/backend/src"

# Set the OpenAI API key (hardcoded for this script)
OPENAI_API_KEY="sk-_ynWP8bFt1E-Lg6ZxIAt8YV1fdB8qU1SMkWCqMVRtmT3BlbkFJ_FWv5x5Oz1lT6vhGwUtODMSKo36FCBHBW30fYvD3sA"
export OPENAI_API_KEY

# Run the Flask app
echo "Running chatbot.py on port 8080..."
python backend/app/chatbot.py

# Step 7: Deactivate the virtual environment after execution
deactivate
echo "Script execution completed."
