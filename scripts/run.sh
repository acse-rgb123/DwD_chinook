#!/bin/bash

# Step 0: Check if Python is installed and at least version 3.6
PYTHON_VERSION=$(python3 --version 2>&1 | grep -Po '(?<=Python )(.+)')

if [[ "$PYTHON_VERSION" < "3.6" ]]; then
    echo "Error: Python 3.6 or higher is required."
    exit 1
fi

# Step 1: Install the required dependencies
echo "Installing dependencies..."

# Install the necessary Python packages, excluding sqlite3 which is part of the standard library
pip install pandas networkx openai python-dotenv PyPDF2 > /dev/null 2>&1

if [ $? -ne 0 ]; then
  echo "Error installing dependencies."
  exit 1
else
  echo "Dependencies installed successfully."
fi

echo "Running main.py..."

# Run the main.py from the src directory
python ./src/main.py

