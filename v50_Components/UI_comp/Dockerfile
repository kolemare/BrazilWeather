# Use Ubuntu as the base image
FROM ubuntu:20.04

# Avoid prompts from apt
ENV DEBIAN_FRONTEND noninteractive

# Install Python, pip, and required system dependencies for Tkinter and matplotlib
RUN apt-get update && \
    apt-get install -y python3 python3-pip python3-tk && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /usr/src/app

# Install required Python packages
RUN pip3 install pandas pyarrow numpy hdfs paho-mqtt==1.6.1 matplotlib

# Copy the UI system and common scripts to the container
COPY /../v50_Components/UI_comp/uisystem.py ./
COPY /../v50_Components/UI_comp/daohandler.py ./
COPY /../v50_Components/UI_comp/comm.py ./

# Ensure the UI system script is executable
RUN chmod +x uisystem.py

# Run the UI system script
CMD ["python3", "./uisystem.py"]