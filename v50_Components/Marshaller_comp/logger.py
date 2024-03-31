import threading
from comm import Comm


class Logger:
    shutdown_event = threading.Event()

    def __init__(self, instance, broker_address):
        self.comm = Comm(instance, broker_address, ["info"])

    @staticmethod
    def write_output(message):
        color_codes = {
            "HDFS": '\033[97m',  # White
            "Processor": '\033[94m',  # Blue
            "UI": '\033[92m',  # Green
            "Loader": '\033[93m',  # Yellow
            "Transformer": '\033[96m',  # Cyan
            "DAO": '\033[95m',  # Purple
            "Marshaller": '\033[90m',  # Black
            "Realtime": '\033[91m'  # Red
        }

        reset_code = '\033[0m'
        prefix = message.split(':')[0]

        color_code = color_codes.get(prefix, reset_code)
        colored_message = f"{color_code}{message}{reset_code}"

        print(colored_message)

    def on_message(self, client, userdata, message):
        if message.topic == "info":
            payload = str(message.payload.decode('utf-8'))
            self.write_output(payload)

    def run(self):
        self.comm.start(self.on_message)
        self.comm.client.subscribe("info")
        Logger.shutdown_event.wait()
        self.comm.stop()

    @staticmethod
    def stop_logger():
        Logger.shutdown_event.set()
