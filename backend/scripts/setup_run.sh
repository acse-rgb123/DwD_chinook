#!/bin/bash

# Check if Docker is installed
if ! command -v docker &> /dev/null
then
    echo "Docker is not installed. Please install Docker and try again."
    exit 1
fi

# Check if Docker Compose is available (using "docker compose" if v2)
if ! docker-compose --version &> /dev/null && ! docker compose version &> /dev/null
then
    echo "Docker Compose is not installed. Please install Docker Compose and try again."
    exit 1
fi

# Determine whether to use 'docker-compose' or 'docker compose' based on Docker Compose version
COMPOSE_COMMAND="docker-compose"
if docker compose version &> /dev/null; then
    COMPOSE_COMMAND="docker compose"
fi

# Build and run using Docker Compose
echo "Building and running with Docker Compose..."
$COMPOSE_COMMAND up --build
