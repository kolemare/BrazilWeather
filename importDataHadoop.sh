#!/bin/bash

# Try to set JAVA_HOME more explicitly
JAVA_PATH=$(update-alternatives --list java | grep java-8 | head -n 1)
if [ -n "$JAVA_PATH" ]; then
    export JAVA_HOME=$(dirname $(dirname "$JAVA_PATH"))
else
    echo "Java 8 could not be found. Please install it and rerun this script."
    exit 1
fi

export PATH=$PATH:$JAVA_HOME/bin
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
export HADOOP_HOME="$SCRIPT_DIR/hadoop"
export PATH=$PATH:$HADOOP_HOME/bin

# Set CLASSPATH for Hadoop libraries
export CLASSPATH=`$HADOOP_HOME/bin/hdfs classpath --glob`

# Define Hadoop service user environment variables
export HDFS_NAMENODE_USER=$(whoami)
export HDFS_DATANODE_USER=$(whoami)
export HDFS_SECONDARYNAMENODE_USER=$(whoami)
export YARN_RESOURCEMANAGER_USER=$(whoami)
export YARN_NODEMANAGER_USER=$(whoami)

# Start Hadoop services
echo "Starting Hadoop services..."
$HADOOP_HOME/sbin/stop-dfs.sh
$HADOOP_HOME/sbin/stop-yarn.sh
$HADOOP_HOME/sbin/start-dfs.sh
$HADOOP_HOME/sbin/start-yarn.sh

hdfs dfsadmin -report

# Optional: Check if the services started successfully
# (Implement checks here if required)

# Set the path to your virtual environment
VENV_PATH="$SCRIPT_DIR/venv"

# Check if the virtual environment path exists
if [ -d "$VENV_PATH" ]; then
    echo "Activating the virtual environment..."
    source "$VENV_PATH/bin/activate"

    # Run your Python script
    echo "Running your Python script..."
    python "$SCRIPT_DIR/importDataHadoop.py"

    # Deactivate the virtual environment
    echo "Deactivating the virtual environment..."
    deactivate
else
    echo "Virtual environment not found at $VENV_PATH. Please set the correct path."
fi

# Stop Hadoop services after the script execution (optional)
echo "Stopping Hadoop services..."
$HADOOP_HOME/sbin/stop-yarn.sh
$HADOOP_HOME/sbin/stop-dfs.sh