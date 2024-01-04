#!/bin/bash

export JAVA_HOME=$(dirname $(dirname $(readlink -f $(which java))))

# Set CLASSPATH for Hadoop libraries
export CLASSPATH=`HADOOP_DIR/bin/hdfs classpath --glob`

# Define Hadoop service user environment variables
export HDFS_NAMENODE_USER=$(whoami)
export HDFS_DATANODE_USER=$(whoami)
export HDFS_SECONDARYNAMENODE_USER=$(whoami)
export YARN_RESOURCEMANAGER_USER=$(whoami)
export YARN_NODEMANAGER_USER=$(whoami)

# Stop YARN Services
$HADOOP_HOME/sbin/stop-yarn.sh

# Stop HDFS Services
$HADOOP_HOME/sbin/stop-dfs.sh

echo "Hadoop services stopped."
