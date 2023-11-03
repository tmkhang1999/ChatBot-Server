#!/bin/bash

set -e

printf "[1] Stopping FastAPI and MariaDB containers...\n"
docker stop chatbot chatbot-db || true

printf "\n[2] Removing FastAPI and MariaDB containers...\n"
docker rm chatbot chatbot-db || true

printf "\n[3] Pruning any dangling Docker images and volumes...\n"
docker image prune -f
docker volume prune -f

printf "\n[4] Building and starting the containers...\n"
docker-compose up -d

# Optional: Display the logs for the FastAPI service
#printf "\n[5] Displaying FastAPI service logs (Ctrl+C to exit)...\n"
#docker-compose logs -f $fastapi_container_name