# Use an appropriate base image
FROM openjdk:8-jdk

# Set environment variables for Hadoop
ENV HADOOP_HOME=/usr/local/hadoop
ENV PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin
ENV HADOOP_CONF_DIR=$HADOOP_HOME/etc/hadoop
ENV HDFS_NAMENODE_USER=root
ENV HDFS_DATANODE_USER=root
ENV HDFS_SECONDARYNAMENODE_USER=root
ENV YARN_RESOURCEMANAGER_USER=root
ENV YARN_NODEMANAGER_USER=root

# Install necessary dependencies
RUN apt-get update && apt-get install -y ssh pdsh

# Copy Hadoop folder from the host to the container
COPY hadoop $HADOOP_HOME

# Copy configuration scripts and make them executable
COPY configureHadoop.sh /usr/local/configureHadoop.sh

RUN chmod +x /usr/local/configureHadoop.sh

COPY clearHadoop.sh /usr/local/clearHadoop.sh
RUN chmod +x /usr/local/configureHadoop.sh

# Set work directory
WORKDIR $HADOOP_HOME

# Run the configuration script
RUN /usr/local/configureHadoop.sh

# Open ports for Hadoop services (adjust as necessary)
EXPOSE 9000

# Default command
CMD ["sh", "-c", "service ssh start; bash"]