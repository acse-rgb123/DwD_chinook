#!/bin/bash

# Step 1: Create backend and frontend directories
mkdir -p backend frontend

# Step 2: Move files and directories to backend
mv app chinook-database-master data docs env notebooks scripts src backend/
mv config.json backend/
mv .env backend/
mv docker-compose.yml backend/

# Step 3: Move frontend-specific directories and files
mv static frontend/
mv templates frontend/
mv index.html frontend/

# Step 4: Update imports and paths in backend Python files
find backend/ -type f -name "*.py" -exec sed -i '' 's/from src\./from backend.src./g' {} +
find backend/ -type f -name "*.py" -exec sed -i '' 's/from app\./from backend.app./g' {} +
find backend/ -type f -name "*.py" -exec sed -i '' 's/import src/import backend.src/g' {} +
find backend/ -type f -name "*.py" -exec sed -i '' 's/import app/import backend.app/g' {} +

# Step 5: Update Flask template and static folder paths in app files
find backend/app/ -type f -name "*.py" -exec sed -i '' "s|template_folder='templates'|template_folder='../../frontend/templates'|g" {} +
find backend/app/ -type f -name "*.py" -exec sed -i '' "s|static_folder='static'|static_folder='../../frontend/static'|g" {} +

# Step 6: Create Dockerfiles for backend and frontend

# Backend Dockerfile
cat <<EOL > backend/Dockerfile
# Use the official Python image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy the backend code into the container
COPY . .

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \\
    pip install --no-cache-dir -r requirements.txt

# Expose port 8000 for the backend
EXPOSE 8000

# Run the backend server
CMD ["python", "app/chatbot.py"]
EOL

# Frontend Dockerfile
cat <<EOL > frontend/Dockerfile
# Use the official Nginx image
FROM nginx:alpine

# Copy static files to the nginx HTML folder
COPY static /usr/share/nginx/html/static
COPY templates /usr/share/nginx/html/templates
COPY index.html /usr/share/nginx/html/index.html

# Expose port 80 for the frontend
EXPOSE 80

# Run Nginx
CMD ["nginx", "-g", "daemon off;"]
EOL

# Step 7: Create docker-compose.yml in the project root to manage both services
cat <<EOL > docker-compose.yml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
    container_name: backend_server
    ports:
      - "8000:8000"
    environment:
      - PYTHONUNBUFFERED=1

  frontend:
    build:
      context: ./frontend
    container_name: frontend_server
    ports:
      - "80:80"
EOL

# Step 8: Notify the user that the process is complete
echo "Project reorganization, Docker setup, and server separation completed. You can now build and run your services using 'docker-compose up --build'."
