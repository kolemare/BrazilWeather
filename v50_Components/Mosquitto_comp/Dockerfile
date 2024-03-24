# Use the official Eclipse Mosquitto image as the base image
FROM eclipse-mosquitto:latest

# Copy your custom configuration file into the container
COPY /../v50_Components/Mosquitto_comp/mosquitto.conf /mosquitto/config/mosquitto.conf

# Expose the MQTT port
EXPOSE 1883

# Run Mosquitto with the custom configuration file
CMD ["/usr/sbin/mosquitto", "-c", "/mosquitto/config/mosquitto.conf"]