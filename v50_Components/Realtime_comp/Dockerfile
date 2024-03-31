# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir paho-mqtt==1.6.1 requests

# Copy the Python script into the container
COPY /../v50_Components/Realtime_comp/comm.py ./
COPY /../v50_Components/Realtime_comp/realtime.py ./
COPY /../v50_Components/Realtime_comp/apikey.json ./
COPY /../v50_Components/Realtime_comp/city_province.json ./
COPY /../v50_Components/Realtime_comp/configuration.json ./


# Run the script when the container launches
CMD ["python", "realtime.py"]