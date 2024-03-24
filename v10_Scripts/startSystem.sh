#!/bin/bash

# Create the Docker network
docker network create docker-network

# Start the MQTT broker container
docker run -d --name mqtt-broker --network docker-network -p 1883:1883 mosquitto-image

# Start the Hadoop container
docker run -it -p 9000:9000 -p 9870:9870 --network docker-network --name hadoop-container hadoop-image

# Start the Loader container
docker run -it --network docker-network --name loader-container loader-image

# Start the Marshaller container
docker run -it --network docker-network --name marshaller-container marshaller-image

# Optional: Start the Transformer container
# docker run -d --network docker-network --name transformer-container transformer-image