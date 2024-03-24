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
RUN apt-get update && apt-get install -y ssh python3 python3-pip
RUN apt-get update && apt-get install -y iputils-ping
RUN pip3 install paho-mqtt==1.6.1

# Copy Hadoop folder from the host to the container
COPY /../v40_Libraries/hadoop $HADOOP_HOME

# Copy configuration, operation scripts, and Python scripts, then make them executable
COPY /../v50_Components/Hadoop_comp/configureHadoop.sh /usr/local/configureHadoop.sh
COPY /../v50_Components/Hadoop_comp/startHadoopServices.sh /usr/local/startHadoopServices.sh
COPY /../v50_Components/Hadoop_comp/stopHadoopServices.sh /usr/local/stopHadoopServices.sh
COPY /../v50_Components/Hadoop_comp/comm.py /usr/local/comm.py
COPY /../v50_Components/Hadoop_comp/hadoop.py /usr/local/hadoop.py
RUN chmod +x /usr/local/configureHadoop.sh /usr/local/startHadoopServices.sh /usr/local/stopHadoopServices.sh /usr/local/comm.py /usr/local/hadoop.py

# Execute the Hadoop configuration script
RUN /usr/local/configureHadoop.sh

# Set work directory
WORKDIR $HADOOP_HOME

# Open ports for Hadoop services
EXPOSE 9000 9870

# Default command
CMD ["python3", "/usr/local/hadoop.py"]