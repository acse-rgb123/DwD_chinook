#!/bin/bash

# Step 1: Check if the virtual environment exists
if [ ! -d "env" ]; then
    echo "Virtual environment not found. Creating a virtual environment..."
    python3 -m venv env

    if [ $? -ne 0 ]; then
        echo "Error: Failed to create virtual environment."
        exit 1
    fi

    # Activate the virtual environment
    source env/bin/activate

    # Step 2: Install dependencies
    echo "Installing dependencies..."
    pip install --upgrade pip > /dev/null 2>&1
    pip install \
        pandas \
        networkx \
        openai==0.28 \
        python-dotenv \
        tabulate \
        PyPDF2 \
        scikit-learn \
        spacy \
        faiss-cpu \
        torch \
        transformers \
        tabulate \
        Flask-SSE \
        Flask \
        flask > /dev/null 2>&1  

    if [ $? -ne 0 ]; then
        echo "Error installing dependencies."
        exit 1
    else
        echo "Dependencies installed successfully."
    fi

    # Step 3: Download the spaCy language model
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
    source env/bin/activate

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
export PYTHONPATH="$PYTHONPATH:$(pwd)/src"

# Set the OpenAI API key (hardcoded for this script)
OPENAI_API_KEY="sk-_ynWP8bFt1E-Lg6ZxIAt8YV1fdB8qU1SMkWCqMVRtmT3BlbkFJ_FWv5x5Oz1lT6vhGwUtODMSKo36FCBHBW30fYvD3sA"
export OPENAI_API_KEY

# Run the chatbot.py script on port 8080
echo "Running chatbot.py on port 8080..."
python app/chatbot.py

# Step 6: Deactivate the virtual environment after execution
deactivate
echo "Script execution completed."
