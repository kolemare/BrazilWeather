# Use an appropriate base image
FROM openjdk:8-jdk

# Find Java Home directory and set JAVA_HOME environment variable
RUN JAVA_HOME_DIR=$(dirname $(dirname $(readlink -f $(which java)))) && \
    echo "export JAVA_HOME=$JAVA_HOME_DIR" >> /etc/profile && \
    . /etc/profile

# Set environment variables for Hadoop
ENV HADOOP_HOME=/usr/local/hadoop
ENV PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin:$JAVA_HOME/bin
ENV HADOOP_CONF_DIR=$HADOOP_HOME/etc/hadoop
ENV HDFS_NAMENODE_USER=root
ENV HDFS_DATANODE_USER=root
ENV HDFS_SECONDARYNAMENODE_USER=root
ENV YARN_RESOURCEMANAGER_USER=root
ENV YARN_NODEMANAGER_USER=root

# Install necessary dependencies
RUN apt-get update && apt-get install -y ssh

# Copy Hadoop folder from the host to the container
COPY hadoop $HADOOP_HOME

# Copy configuration and operation scripts and make them executable
COPY configureHadoop.sh /usr/local/configureHadoop.sh
COPY startHadoopServices.sh /usr/local/startHadoopServices.sh
COPY stopHadoopServices.sh /usr/local/stopHadoopServices.sh
RUN chmod +x /usr/local/configureHadoop.sh /usr/local/startHadoopServices.sh /usr/local/stopHadoopServices.sh

RUN /usr/local/configureHadoop.sh

# Set work directory
WORKDIR $HADOOP_HOME

# Open ports for Hadoop services (adjust as necessary)
EXPOSE 9000

# Default command
CMD ["sh", "-c", "service ssh start; bash"]