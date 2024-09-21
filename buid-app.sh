#!/bin/bash

set -e

printf "[1] Stopping and removing FastAPI and MariaDB containers, networks, and volumes...\n"
docker-compose down -v

printf "\n[2] Pruning any dangling Docker images...\n"
docker image prune -f

printf "\n[3] Building and starting the containers...\n"
docker-compose up -d