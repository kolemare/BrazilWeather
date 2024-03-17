
# Navigate to the script's directory
cd "$(dirname "$0")/.."

# Prune all unused Docker objects
yes | docker system prune -a

# Build the Hadoop image
docker build -t hadoop-image -f ./v50_Components/Hadoop_comp/Hadoop.dockerfile .

# Build the Hadoop Loader image
docker build -t loader-hadoop-image -f ./v50_Components/Loader_comp/HadoopLoader.dockerfile .

# List Docker images
docker images