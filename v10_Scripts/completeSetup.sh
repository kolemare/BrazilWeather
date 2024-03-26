#!/bin/bash

# Get the directory of the script
SCRIPT_DIR=$(dirname "$(realpath "$BASH_SOURCE")")

# Navigate to the root of the repository
cd "$SCRIPT_DIR/.."

# Update package list
echo "Updating package list..."
sudo apt update -y

# Install Java (required for Hadoop and Kafka)
echo "Checking for Java installation..."
if type -p java; then
    JAVA_VERSION=$(java -version 2>&1 | awk -F '"' '/version/ {print $2}')
    if [[ "$JAVA_VERSION" < "1.8" ]]; then
        echo "Installing Java..."
        sudo apt-get install -y openjdk-8-jdk
    else
        echo "A suitable version of Java is already installed."
    fi
else
    echo "Java not found. Installing Java..."
    sudo apt-get install -y openjdk-8-jdk
fi

# Set JAVA_HOME
echo "Setting JAVA_HOME..."
JAVA_HOME=$(dirname $(dirname $(readlink -f $(which java))))
echo "export JAVA_HOME=$JAVA_HOME" >> ~/.bashrc
source ~/.bashrc

# Install Python 3.10 if it's not installed
if ! command -v python3.10 &> /dev/null; then
    echo "Python 3.10 not found. Installing Python 3.10..."
    sudo apt install -y python3.10
else
    echo "Python 3.10 is already installed."
fi

# Install python3.10-venv to ensure the venv module works correctly
echo "Installing python3.10-venv..."
sudo apt install -y python3.10-venv

# Install build-essential and other dependencies for Python packages
echo "Installing build dependencies..."
sudo apt-get install -y build-essential libssl-dev libffi-dev python3.10-dev libyaml-dev

# Set the name of the virtual environment
VENV_NAME="venv"
AIRFLOW_VERSION="2.8.0"
AIRFLOW_HOME="$(pwd)/v40_Libraries/airflow"

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_NAME" ]; then
    echo "Creating virtual environment..."
    python3.10 -m venv $VENV_NAME
else
    echo "Virtual environment already exists."
fi

# Activate the virtual environment
echo "Activating the virtual environment..."
source $VENV_NAME/bin/activate

# Upgrade pip to the latest version
pip install --upgrade pip

# Install required libraries
echo "Installing required libraries..."
pip install google-api-python-client google-auth-oauthlib google-auth-httplib2 pandas pyarrow numpy hdfs paho-mqtt==1.6.1 matplotlib

# Install Apache Airflow
echo "Installing Apache Airflow..."
AIRFLOW_GPL_UNIDECODE=yes pip install apache-airflow==$AIRFLOW_VERSION

# Initialize Airflow (create default config and database)
echo "Initializing Apache Airflow..."
export AIRFLOW_HOME

# Determine the path to the 'hadoop' directory
HADOOP_DIR="$(pwd)/v40_Libraries/hadoop"

# Check if Hadoop is already installed
if [ ! -d "$HADOOP_DIR" ]; then
    # Download Hadoop
    echo "Downloading Hadoop..."
    wget https://downloads.apache.org/hadoop/common/hadoop-3.3.6/hadoop-3.3.6.tar.gz

    # Extract Hadoop
    echo "Extracting Hadoop..."
    tar -xzvf hadoop-3.3.6.tar.gz
    rm hadoop-3.3.6.tar.gz

    # Move Hadoop to the project directory
    echo "Moving Hadoop to the project directory..."
    mv hadoop-3.3.6 $HADOOP_DIR

    # Set Hadoop environment variables
    echo "Setting Hadoop environment variables..."
    export HADOOP_HOME=$HADOOP_DIR
    export PATH=$PATH:$HADOOP_HOME/bin
    echo "export HADOOP_HOME=$HADOOP_DIR" >> ~/.bashrc
    echo "export PATH=$PATH:$HADOOP_HOME/bin" >> ~/.bashrc
fi

# Kafka installation directory
KAFKA_DIR="$(pwd)/v40_Libraries/kafka"

# Check if Kafka is already installed
if [ ! -d "$KAFKA_DIR" ]; then
    # Download Kafka
    echo "Downloading Kafka..."
    wget https://downloads.apache.org/kafka/3.6.1/kafka_2.13-3.6.1.tgz

    # Extract Kafka
    echo "Extracting Kafka..."
    tar -xzvf kafka_2.13-3.6.1.tgz
    rm kafka_2.13-3.6.1.tgz

    # Move Kafka to the project directory
    echo "Moving Kafka to the project directory..."
    mv kafka_2.13-3.6.1 $KAFKA_DIR
fi

# Install SQLite
echo "Checking for SQLite installation..."
if ! command -v sqlite3 &> /dev/null; then
    echo "SQLite not found. Installing SQLite..."
    sudo apt-get install -y sqlite3
else
    echo "SQLite is already installed."
fi

# Deactivate the virtual environment
echo "Deactivating the virtual environment..."
deactivate

# Complete setup
echo "Setup is complete."