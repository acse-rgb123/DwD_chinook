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
    faiss-cpu > /dev/null 2>&1

if [ $? -ne 0 ]; then
  echo "Error installing dependencies."
  exit 1
else
  echo "Dependencies installed successfully."
fi

# Step 4: Run main.py from the src directory
echo "Running main.py..."
python ./src/main.py

# Step 5: Deactivate the virtual environment after execution
deactivate
