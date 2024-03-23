# Navigate to the script's directory
cd "$(dirname "$0")/.."

# Prune all unused Docker objects
yes | docker system prune -a

# Build the Hadoop image
docker build -t hadoop-image -f ./v50_Components/Hadoop_comp/Dockerfile .

# Build the Hadoop Loader image
docker build -t loader-image -f ./v50_Components/Loader_comp/Dockerfile .

# Build the Transformer image
docker build -t transformer-image -f ./v50_Components/Transformer_comp/Dockerfile .

# List Docker images
docker images