# Use Ubuntu as the base image
FROM ubuntu:20.04

# Avoid prompts from apt
ENV DEBIAN_FRONTEND noninteractive

# Install Python, pip, and OpenJDK 8
RUN apt-get update && \
    apt-get install -y python3 python3-pip openjdk-8-jdk && \
    rm -rf /var/lib/apt/lists/*

# Set JAVA_HOME environment variable
ENV JAVA_HOME /usr/lib/jvm/java-8-openjdk-amd64/
ENV PATH $JAVA_HOME/bin:$PATH

# Set the working directory in the container
WORKDIR /usr/src/app

# Install required Python packages
RUN pip3 install pandas pyarrow hdfs

# Copy the Python script and dataset directory to the container
COPY importDataHadoop.py ./
COPY ./dataset/ ./dataset/

# Ensure your Python script is executable
RUN chmod +x importDataHadoop.py

# Default command: Run the Python script
CMD ["python3", "./importDataHadoop.py"]

# The command to start a Bash shell
CMD ["/bin/bash"]