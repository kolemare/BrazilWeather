from paho.mqtt.client import Client as MQTTClient


class Comm:
    def __init__(self, instance, broker_address, topics):
        self.broker_address = broker_address
        self.topics = topics
        self.client = MQTTClient(client_id=instance)
        self.client.on_message = None

    def send_info(self, message):
        self.client.publish("info", f"Marshaller: {message}")

    def start(self, callback):
        self.client.on_message = callback
        self.client.connect(self.broker_address)
        for topic in self.topics:
            self.client.subscribe(topic)
        self.client.loop_start()

    def stop(self):
        self.client.loop_stop()
        self.client.disconnect()
