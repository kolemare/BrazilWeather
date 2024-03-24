#!/bin/bash

# Stop all running Docker containers
docker stop $(docker ps -aq)

# Remove all Docker containers
docker rm $(docker ps -aq)

# Remove all Docker images
docker rmi $(docker images -q)

# Remove all Docker networks
docker network prune -f

# Navigate to the script's directory
cd "$(dirname "$0")/.."

# Prune all unused Docker objects
yes | docker system prune -a

# Build the custom Mosquitto MQTT broker image
docker build -t mosquitto-image -f ./v50_Components/Mosquitto_comp/Dockerfile .

# Build the Hadoop image
docker build -t hadoop-image -f ./v50_Components/Hadoop_comp/Dockerfile .

# Build the Loader image
docker build -t loader-image -f ./v50_Components/Loader_comp/Dockerfile .

# Build the Transformer image
docker build -t transformer-image -f ./v50_Components/Transformer_comp/Dockerfile .

# Build the Marshaller image
docker build -t marshaller-image -f ./v50_Components/Marshaller_comp/Dockerfile .

# List Docker images
docker images