#!/bin/bash

# Step 0: Check if Python is installed and at least version 3.6
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
REQUIRED_VERSION="3.6"
if [[ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]]; then
    echo "Error: Python 3.6 or higher is required."
    exit 1
fi

# Step 1: Create a virtual environment
echo "Creating virtual environment..."
python3 -m venv env

if [ $? -ne 0 ]; then
  echo "Error: Failed to create virtual environment."
  exit 1
fi

# Step 2: Activate the virtual environment
source env/bin/activate

# Step 3: Install the required dependencies
echo "Installing dependencies..."
pip install --upgrade pip > /dev/null 2>&1

# Installing required Python packages
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
    transformers > /dev/null 2>&1

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

# Step 5: Set the OpenAI API key from an environment variable or prompt the user
# Step 5: Hardcode the OpenAI API key
OPENAI_API_KEY="sk-_ynWP8bFt1E-Lg6ZxIAt8YV1fdB8qU1SMkWCqMVRtmT3BlbkFJ_FWv5x5Oz1lT6vhGwUtODMSKo36FCBHBW30fYvD3sA"

# Export the API key so it can be accessed by Python
export OPENAI_API_KEY

# Step 6: Run main.py from the src directory
echo "Running main.py..."
python ./src/main.py

# Step 7: Deactivate the virtual environment after execution
deactivate
