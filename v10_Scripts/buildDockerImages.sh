#!/bin/bash

# Navigate to the script's directory
cd "$(dirname "$0")/.."

# Check for flags
if [ $# -eq 0 ]; then
    docker stop $(docker ps -aq)

    # Remove all Docker containers
    docker rm $(docker ps -aq)

    # Remove all Docker images
    docker rmi $(docker images -q)

    # Build all Docker images if no flags provided
    docker build -t marshaller-image -f ./v50_Components/Marshaller_comp/Dockerfile .
    docker build -t loader-image -f ./v50_Components/Loader_comp/Dockerfile .
    docker build -t transformer-image -f ./v50_Components/Transformer_comp/Dockerfile .
    docker build -t processor-image -f ./v50_Components/Processor_comp/Dockerfile .
    docker build -t hadoop-image -f ./v50_Components/Hadoop_comp/Dockerfile .
    docker build -t mosquitto-image -f ./v50_Components/Mosquitto_comp/Dockerfile .
else
    # Process flags
    while [ $# -gt 0 ]; do
        case "$1" in
            --clean)
                # Prune all unused Docker objects
                yes | docker system prune -a
                docker build -t marshaller-image -f ./v50_Components/Marshaller_comp/Dockerfile .
                docker build -t loader-image -f ./v50_Components/Loader_comp/Dockerfile .
                docker build -t transformer-image -f ./v50_Components/Transformer_comp/Dockerfile .
                docker build -t processor-image -f ./v50_Components/Processor_comp/Dockerfile .
                docker build -t hadoop-image -f ./v50_Components/Hadoop_comp/Dockerfile .
                docker build -t mosquitto-image -f ./v50_Components/Mosquitto_comp/Dockerfile .
                ;;
            --marshaller)
                docker stop marshaller-container
                docker rm marshaller-container
                docker rmi marshaller-container
                docker build -t marshaller-image -f ./v50_Components/Marshaller_comp/Dockerfile .
                ;;
            --loader)
                docker stop loader-container
                docker rm loader-container
                docker rmi loader-container
                docker build -t loader-image -f ./v50_Components/Loader_comp/Dockerfile .
                ;;
            --transformer)
                docker stop transformer-container
                docker rm transformer-container
                docker rmi transformer-container
                docker build -t transformer-image -f ./v50_Components/Transformer_comp/Dockerfile .
                ;;
            --processor)
                docker stop processor-container
                docker rm processor-container
                docker rmi processor-container
                docker build -t processor-image -f ./v50_Components/Processor_comp/Dockerfile .
                ;;
            --hdfs)
                docker stop hdfs-container
                docker rm hdfs-container
                docker rmi hdfs-container
                docker build -t hadoop-image -f ./v50_Components/Hadoop_comp/Dockerfile .
                ;;
            --mqqt)
                docker stop mqtt-broker
                docker rm mqtt-broker
                docker rmi mqtt-broker
                docker build -t mosquitto-image -f ./v50_Components/Mosquitto_comp/Dockerfile .
                ;;
            *)
                echo "Invalid flag: $1"
                ;;
        esac
        shift
    done
fi

docker images | grep -v "latest" | awk '{print $3}' | xargs docker rmi

# List Docker images
docker images