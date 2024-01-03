#!/bin/bash

# Variables
REPO_ROOT="$(pwd)"
HADOOP_DIR="$REPO_ROOT/hadoop"
HADOOP_BIN="$HADOOP_DIR/bin" # Add Hadoop bin directory
NAMENODE_DIR="$HADOOP_DIR/hdfs/namenode"
DATANODE_DIR="$HADOOP_DIR/hdfs/datanode"
HADOOP_CONF_DIR="$HADOOP_DIR/etc/hadoop"
HADOOP_ENV_SH="$HADOOP_CONF_DIR/hadoop-env.sh"

# Add Hadoop bin directory to PATH
export PATH=$PATH:$HADOOP_BIN

# Determine JAVA_HOME
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

# Configure core-site.xml
if [ -f "$CORE_SITE" ]; then
    configure_xml "$CORE_SITE" "fs.defaultFS" "hdfs://localhost:9000"
else
    echo "Error: $CORE_SITE does not exist."
    exit 1
fi

# Configure hdfs-site.xml
if [ -f "$HDFS_SITE" ]; then
    configure_xml "$HDFS_SITE" "dfs.replication" "1"
    configure_xml "$HDFS_SITE" "dfs.namenode.name.dir" "$NAMENODE_DIR"
    configure_xml "$HDFS_SITE" "dfs.datanode.data.dir" "$DATANODE_DIR"
else
    echo "Error: $HDFS_SITE does not exist."
    exit 1
fi

hdfs namenode -format

# Check for SSH keys and create them if they don't exist
SSH_DIR="$HOME/.ssh"
KEY_FILE="$SSH_DIR/id_rsa"

# Install and start SSH server if not already running
if ! systemctl is-active --quiet ssh; then
    sudo apt-get update
    sudo apt-get install -y openssh-server
    sudo systemctl start ssh
fi

# Ensure SSH can connect to localhost
if ! ssh -o BatchMode=yes -o ConnectTimeout=5 localhost 'echo SSH to localhost works'; then
    mkdir -p "$SSH_DIR"
    chmod 700 "$SSH_DIR"

    if [ ! -f "$KEY_FILE" ]; then
        ssh-keygen -t rsa -P '' -f "$KEY_FILE"
    fi

    if ! grep -q "$(cat "$KEY_FILE.pub")" "$SSH_DIR/authorized_keys" 2>/dev/null; then
        cat "$KEY_FILE.pub" >> "$SSH_DIR/authorized_keys"
    fi

    chmod 600 "$SSH_DIR/authorized_keys"
    echo "SSH configured for passwordless access to localhost."
else
    echo "SSH to localhost is already configured."
fi

echo "Hadoop configuration completed."
