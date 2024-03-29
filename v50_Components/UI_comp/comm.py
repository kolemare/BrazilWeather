from paho.mqtt.client import Client

class Comm:
    def __init__(self, broker_address, request_topic1, request_topic2, response_topic):
        self.broker_address = broker_address
        self.request_topic1 = request_topic1
        self.request_topic2 = request_topic2
        self.response_topic = response_topic
        self.client = Client(client_id="ui")
        self.client.on_message = self.on_message
        self.callback = None

    def on_message(self, client, userdata, message):
        payload = str(message.payload.decode('utf-8'))
        print(f"UISystem: Received request: {payload}")

        if self.callback:
            response = self.callback(payload, message.topic)
            if response is not None:
                self.client.publish(self.response_topic, response)

    def send_info(self, message):
        self.client.publish("info", "UI: " + str(message))

    def start(self, callback):
        self.callback = callback
        self.client.connect(self.broker_address)
        self.client.subscribe(self.request_topic1)
        self.client.subscribe(self.request_topic2)
        self.client.loop_start()

    def stop(self):
        self.client.loop_stop()
        self.client.disconnect()
