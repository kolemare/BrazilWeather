#!/bin/bash

# Variables
HADOOP_DIR="/usr/local/hadoop" # Adjusted to match Dockerfile path
NAMENODE_DIR="$HADOOP_DIR/hdfs/namenode"
DATANODE_DIR="$HADOOP_DIR/hdfs/datanode"
HADOOP_CONF_DIR="$HADOOP_DIR/etc/hadoop"
HADOOP_ENV_SH="$HADOOP_CONF_DIR/hadoop-env.sh"

# Determine JAVA_HOME (Java should already be set up in the Docker image)
JAVA_HOME_VALUE=$(dirname $(dirname $(readlink -f $(which java))))

# Update hadoop-env.sh with JAVA_HOME
if [ -f "$HADOOP_ENV_SH" ]; then
    if grep -q "^export JAVA_HOME=" "$HADOOP_ENV_SH"; then
        sed -i "s|^export JAVA_HOME=.*|export JAVA_HOME=$JAVA_HOME_VALUE|" "$HADOOP_ENV_SH"
        echo "Updated JAVA_HOME in $HADOOP_ENV_SH"
    else
        echo "export JAVA_HOME=$JAVA_HOME_VALUE" >> "$HADOOP_ENV_SH"
        echo "Set JAVA_HOME in $HADOOP_ENV_SH"
    fi
else
    echo "Error: $HADOOP_ENV_SH does not exist."
    exit 1
fi

# Create NameNode and DataNode directories
mkdir -p "$NAMENODE_DIR" "$DATANODE_DIR"
echo "Created Hadoop directories."

# Function to configure an XML file
configure_xml() {
    local file=$1
    local property=$2
    local value=$3

    # Check if the property already exists
    if grep -q "<name>$property</name>" "$file"; then
        # Property exists, update the value
        sed -i "/<name>$property<\/name>/!b;n;c<value>$value<\/value>" "$file"
        echo "Updated $property in $file"
    else
        # Property does not exist, add property
        sed -i "/<\/configuration>/i \ \ \ <property>\n\t<name>$property</name>\n\t<value>$value</value>\n\t</property>" "$file"
        echo "Added $property to $file"
    fi
}

# Configure core-site.xml and hdfs-site.xml
CORE_SITE="$HADOOP_CONF_DIR/core-site.xml"
HDFS_SITE="$HADOOP_CONF_DIR/hdfs-site.xml"

configure_xml "$CORE_SITE" "fs.defaultFS" "hdfs://localhost:9000"
configure_xml "$HDFS_SITE" "dfs.replication" "1"
configure_xml "$HDFS_SITE" "dfs.namenode.name.dir" "$NAMENODE_DIR"
configure_xml "$HDFS_SITE" "dfs.datanode.data.dir" "$DATANODE_DIR"

# Format the NameNode (this should be done carefully, only when needed)
hdfs namenode -format

echo "Hadoop configuration completed."
