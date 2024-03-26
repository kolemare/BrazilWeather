#!/bin/bash

# Stop all running Docker containers
docker stop $(docker ps -aq)

# Remove all Docker containers
docker rm $(docker ps -aq)

# Remove all Docker networks
docker network prune -f

# Create the Docker network
docker network create docker-network

# Start the MQTT broker container
docker run -d -p 1883:1883 --network docker-network --name mqtt-broker mosquitto-image

# Start the Hadoop container
docker run -d -p 9000:9000 -p 9870:9870 --network docker-network --name hadoop-container hadoop-image

# Start the Loader container
docker run -d --network docker-network --name loader-container loader-image

# Start the Transformer container
docker run -d --network docker-network --name transformer-container transformer-image

# Start the Processor container
docker run -d --network docker-network --name processor-container processor-image

# Start the Marshaller container
docker run -it --network docker-network --name marshaller-container marshaller-image