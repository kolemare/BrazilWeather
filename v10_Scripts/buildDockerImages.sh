#!/bin/bash

# Navigate to the script's directory
cd "$(dirname "$0")/.."

# Stop all running Docker containers
docker stop -f $(docker ps -aq)

# Remove all Docker containers
docker rm -f $(docker ps -aq)

# Remove dangling images
docker images --quiet --filter "dangling=true" | xargs --no-run-if-empty sudo docker rmi -f


# Check for flags
if [ $# -eq 0 ]; then
    # Build all Docker images if no flags provided
    docker build -t marshaller-image -f ./v50_Components/Marshaller_comp/Dockerfile .
    docker build -t loader-image -f ./v50_Components/Loader_comp/Dockerfile .
    docker build -t transformer-image -f ./v50_Components/Transformer_comp/Dockerfile .
    docker build -t processor-image -f ./v50_Components/Processor_comp/Dockerfile .
    docker build -t hadoop-image -f ./v50_Components/Hadoop_comp/Dockerfile .
    docker build -t mosquitto-image -f ./v50_Components/Mosquitto_comp/Dockerfile .
    docker build -t realtime-image -f ./v50_Components/Realtime_comp/Dockerfile .
    docker build -t ui-image -f ./v50_Components/UI_comp/Dockerfile .
else
    # Process flags
    while [ $# -gt 0 ]; do
        case "$1" in
            --clean)
                # Remove all Docker images
                docker rmi -f $(docker images -q)

                # Prune all unused Docker objects
                yes | docker system prune -a
                docker build -t marshaller-image -f ./v50_Components/Marshaller_comp/Dockerfile .
                docker build -t loader-image -f ./v50_Components/Loader_comp/Dockerfile .
                docker build -t transformer-image -f ./v50_Components/Transformer_comp/Dockerfile .
                docker build -t processor-image -f ./v50_Components/Processor_comp/Dockerfile .
                docker build -t hadoop-image -f ./v50_Components/Hadoop_comp/Dockerfile .
                docker build -t mosquitto-image -f ./v50_Components/Mosquitto_comp/Dockerfile .
                docker build -t realtime-image -f ./v50_Components/Realtime_comp/Dockerfile .
                docker build -t ui-image -f ./v50_Components/UI_comp/Dockerfile .
                ;;
            --marshaller)
                IMAGE_ID=$(docker images --format "{{.ID}}" --filter=reference="marshaller-image")
                docker stop marshaller-container
                docker rm marshaller-container
                docker rmi $IMAGE_ID
                docker build -t marshaller-image -f ./v50_Components/Marshaller_comp/Dockerfile .
                ;;
            --loader)
                IMAGE_ID=$(docker images --format "{{.ID}}" --filter=reference="loader-image")
                docker stop loader-container
                docker rm loader-container
                docker rmi $IMAGE_ID
                docker build -t loader-image -f ./v50_Components/Loader_comp/Dockerfile .
                ;;
            --transformer)
                IMAGE_ID=$(docker images --format "{{.ID}}" --filter=reference="transformer-image")
                docker stop transformer-container
                docker rm transformer-container
                docker rmi $IMAGE_ID
                docker build -t transformer-image -f ./v50_Components/Transformer_comp/Dockerfile .
                ;;
            --processor)
                IMAGE_ID=$(docker images --format "{{.ID}}" --filter=reference="processor-image")
                docker stop processor-container
                docker rm processor-container
                docker rmi $IMAGE_ID
                docker build -t processor-image -f ./v50_Components/Processor_comp/Dockerfile .
                ;;
            --hdfs)
                IMAGE_ID=$(docker images --format "{{.ID}}" --filter=reference="hadoop-image")
                docker stop hdfs-container
                docker rm hdfs-container
                docker rmi $IMAGE_ID
                docker build -t hadoop-image -f ./v50_Components/Hadoop_comp/Dockerfile .
                ;;
            --mqtt)
                IMAGE_ID=$(docker images --format "{{.ID}}" --filter=reference="mosquitto-image")
                docker stop mqtt-broker
                docker rm mqtt-broker
                docker rmi $IMAGE_ID
                docker build -t mosquitto-image -f ./v50_Components/Mosquitto_comp/Dockerfile .
                ;;
            --realtime)
                IMAGE_ID=$(docker images --format "{{.ID}}" --filter=reference="realtime-image")
                docker stop realtime-container
                docker rm realtime-container
                docker rmi $IMAGE_ID
                docker build -t realtime-image -f ./v50_Components/Realtime_comp/Dockerfile .
                ;;
            --ui)
                IMAGE_ID=$(docker images --format "{{.ID}}" --filter=reference="ui-image")
                docker stop ui-container
                docker rm ui-container
                docker rmi $IMAGE_ID
                docker build -t ui-image -f ./v50_Components/UI_comp/Dockerfile .
                ;;
            *)
                echo "Invalid flag: $1"
                ;;
        esac
        shift
    done
fi

docker images | grep -v "latest" | awk '{print $3}' | xargs docker rmi -f

# List Docker images
docker images