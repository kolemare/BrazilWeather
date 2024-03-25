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
RUN pip3 install pandas pyarrow numpy hdfs paho-mqtt==1.6.1

# Copy the transformer script to the container
COPY /../v50_Components/Transformer_comp/transformer.py ./
COPY /../v50_Components/Transformer_comp/comm.py ./

# Ensure the transformer script is executable
RUN chmod +x transformer.py

# Default command: Run the transformer script
CMD ["python3", "./transformer.py"]