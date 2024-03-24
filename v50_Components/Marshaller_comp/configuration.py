import json
import threading


class Config:
    def __init__(self, config_file='configuration.json'):
        self.lock = threading.Lock()

        with open(config_file, 'r') as file:
            json_config = json.load(file)

        # Extract configuration values
        self._data = json_config['data']
        self._time_threshold = json_config['max_wait_time']
        self._hadoop_boot = json_config['hadoop_boot']
        self._port = json_config['port']

        # Global variables
        self._hadoop_status = False
        self._response_events = {}
        self._transformer_task = []
        self._transformed = 0

    @property
    def data(self):
        with self.lock:
            return self._data

    @data.setter
    def data(self, value):
        with self.lock:
            self._data = value

    @property
    def time_threshold(self):
        with self.lock:
            return self._time_threshold

    @time_threshold.setter
    def time_threshold(self, value):
        with self.lock:
            self._time_threshold = value

    @property
    def hadoop_boot(self):
        with self.lock:
            return self._hadoop_boot

    @hadoop_boot.setter
    def hadoop_boot(self, value):
        with self.lock:
            self._hadoop_boot = value

    @property
    def port(self):
        with self.lock:
            return self._port

    @port.setter
    def port(self, value):
        with self.lock:
            self._port = value

    @property
    def hadoop_status(self):
        with self.lock:
            return self._hadoop_status

    @hadoop_status.setter
    def hadoop_status(self, value):
        with self.lock:
            self._hadoop_status = value

    @property
    def response_events(self):
        with self.lock:
            return self._response_events

    @response_events.setter
    def response_events(self, value):
        with self.lock:
            self._response_events = value

    @property
    def transformer_task(self):
        with self.lock:
            return self._transformer_task

    @transformer_task.setter
    def transformer_task(self, value):
        with self.lock:
            self._transformer_task = value

    @property
    def transformed(self):
        with self.lock:
            return self._transformed

    @transformed.setter
    def transformed(self, value):
        with self.lock:
            self._transformed = value


# Create a singleton instance of the Config class
config = Config()
