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
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
export HADOOP_HOME="$ROOT_DIR/v40_Libraries/hadoop"
export PATH=$PATH:$HADOOP_HOME/bin

# Set CLASSPATH for Hadoop libraries
export CLASSPATH=`$HADOOP_HOME/bin/hdfs classpath --glob`

# Define Hadoop service user environment variables
export HDFS_NAMENODE_USER=$(whoami)
export HDFS_DATANODE_USER=$(whoami)
export HDFS_SECONDARYNAMENODE_USER=$(whoami)
export YARN_RESOURCEMANAGER_USER=$(whoami)
export YARN_NODEMANAGER_USER=$(whoami)

hdfs dfsadmin -report

# Optional: Check if the services started successfully
# (Implement checks here if required)

# Set the path to your virtual environment (in the root of the repository)
VENV_PATH="$ROOT_DIR/venv"

# Check if the virtual environment path exists
if [ -d "$VENV_PATH" ]; then
    echo "Activating the virtual environment..."
    source "$VENV_PATH/bin/activate"

    # Run your Python script
    echo "Running your Python script..."
    python "$ROOT_DIR/v20_Test/processData.py"

    # Deactivate the virtual environment
    echo "Deactivating the virtual environment..."
    deactivate
else
    echo "Virtual environment not found at $VENV_PATH. Please set the correct path."
fi