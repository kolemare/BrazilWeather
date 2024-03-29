#!/bin/bash

# Stop all running Docker containers
docker stop $(docker ps -aq) -f

# Remove all Docker containers
docker rm $(docker ps -aq) -f

# Remove all Docker networks
docker network prune -f

# Create the Docker network
docker network create docker-network

# Start the MQTT broker container
docker run -d -p 1883:1883 --network docker-network --name mqtt-broker mosquitto-image
mqtt_ip=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' mqtt-broker)

# Start the Hadoop container
docker run -d --rm --network docker-network --name hadoop-container -p 9000:9000 -p 9870:9870 hadoop-image

# Start the Loader container
docker run -d --rm --network docker-network --name loader-container loader-image

# Start the Transformer container
docker run -d --rm --network docker-network --name transformer-container transformer-image

# Start the Processor container
docker run -d --rm --network docker-network --name processor-container processor-image

# Start the UI container, passing the MQTT broker's IP address
xhost +local:docker
docker run -d --rm --name ui-container --net=host -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix -e MQTT_BROKER_IP=$mqtt_ip ui-image

# Start the Marshaller container in interactive mode
docker run -it --rm --network docker-network --name marshaller-container marshaller-image
xhost -local:docker
