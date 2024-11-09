# Use the official Python image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy the backend code into the container
COPY . .

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Expose port 8000 for the backend
EXPOSE 8000

# Run the backend server
CMD ["python", "app/chatbot.py"]
