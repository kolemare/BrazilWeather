from paho.mqtt.client import Client, MQTTv5

class Comm:
    def __init__(self, broker_address, request_topic, response_topic):
        self.broker_address = broker_address
        self.request_topic = request_topic
        self.response_topic = response_topic
        self.client = Client(client_id="hdfs")
        self.client.on_message = self.on_message
        self.callback = None

    def on_message(self, client, userdata, message):
        payload = str(message.payload.decode('utf-8'))
        print(f"HDFS: Received request: {payload}")

        if self.callback:
            response = self.callback(payload)
            if response is not None:
                self.client.publish(self.response_topic, response)

    def start(self, callback):
        self.callback = callback
        self.client.connect(self.broker_address)
        self.client.subscribe(self.request_topic)
        self.client.loop_start()

    def stop(self):
        self.client.loop_stop()
        self.client.disconnect()