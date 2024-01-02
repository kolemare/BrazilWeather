#!/bin/bash

# Variables
REPO_ROOT="$(pwd)"
HADOOP_DIR="$REPO_ROOT/hadoop"
NAMENODE_DIR="$HADOOP_DIR/hdfs/namenode"
DATANODE_DIR="$HADOOP_DIR/hdfs/datanode"
HADOOP_CONF_DIR="$HADOOP_DIR/etc/hadoop"

# Create NameNode and DataNode directories if they don't exist
if [ ! -d "$NAMENODE_DIR" ]; then
    mkdir -p "$NAMENODE_DIR"
    echo "Created NameNode directory at $NAMENODE_DIR"
fi

if [ ! -d "$DATANODE_DIR" ]; then
    mkdir -p "$DATANODE_DIR"
    echo "Created DataNode directory at $DATANODE_DIR"
fi

# Function to configure an XML file
configure_xml() {
    local file=$1
    local property=$2
    local value=$3

    if grep -q "<name>$property</name>" "$file"; then
        # Property exists, replace its value
        sed -i "s|<value>.*</value>|<value>$value</value>|g" "$file"
        echo "Updated $property in $file"
    else
        # Property does not exist, add it
        sed -i "/<\/configuration>/i \ \ \ <property>\n\t<name>$property</name>\n\t<value>$value</value>\n\t</property>" "$file"
        echo "Added $property to $file"
    fi
}

# Configure core-site.xml
CORE_SITE="$HADOOP_CONF_DIR/core-site.xml"
if [ -f "$CORE_SITE" ]; then
    configure_xml "$CORE_SITE" "fs.defaultFS" "hdfs://localhost:9000"
else
    echo "Error: $CORE_SITE does not exist."
fi

# Configure hdfs-site.xml
HDFS_SITE="$HADOOP_CONF_DIR/hdfs-site.xml"
if [ -f "$HDFS_SITE" ]; then
    configure_xml "$HDFS_SITE" "dfs.replication" "1"
    configure_xml "$HDFS_SITE" "dfs.namenode.name.dir" "file://$NAMENODE_DIR"
    configure_xml "$HDFS_SITE" "dfs.datanode.data.dir" "file://$DATANODE_DIR"
else
    echo "Error: $HDFS_SITE does not exist."
fi

echo "Hadoop configuration completed."
