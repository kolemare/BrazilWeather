#!/bin/bash

export JAVA_HOME=$(dirname $(dirname $(readlink -f $(which java))))

xport CLASSPATH=`$HADOOP_HOME/bin/hdfs classpath --glob`

/etc/init.d/ssh start
yes | hdfs dfsadmin -report

yes | hdfs namenode -format

# Start HDFS Services
$HADOOP_HOME/sbin/start-dfs.sh

# Start YARN Services
$HADOOP_HOME/sbin/start-yarn.sh

hdfs dfsadmin -report

echo "Hadoop services started."
