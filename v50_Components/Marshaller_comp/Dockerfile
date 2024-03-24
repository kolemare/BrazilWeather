# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir paho-mqtt==1.6.1

# Copy the Python script into the container
COPY /../v50_Components/Marshaller_comp/marshaller.py ./
COPY /../v50_Components/Marshaller_comp/configuration.py ./
COPY /../v50_Components/Marshaller_comp/configuration.json ./

# Expose a port
EXPOSE 1883

# Run the script when the container launches
CMD ["python", "marshaller.py"]