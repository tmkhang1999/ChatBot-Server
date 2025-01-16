#!/bin/bash
set -e

# Check if Docker daemon is running
if ! docker info > /dev/null 2>&1; then
    echo "Docker daemon is not running"
    exit 1
fi

printf "[1] Stopping and removing current containers...\n"
docker-compose down -v || {
    echo "Failed to stop containers"
    exit 1
}

printf "\n[2] Pruning any dangling Docker images...\n"
docker image prune -f || {
    echo "Failed to prune images"
    exit 1
}

printf "\n[3] Building and starting the containers...\n"
docker-compose up -d || {
    echo "Failed to start containers"
    exit 1
}