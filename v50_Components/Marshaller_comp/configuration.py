import json
import queue
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
        self.batch_tasks = json_config['batch_tasks']

        # Global variables
        self._hadoop_status = False
        self._system_shutdown = False
        self._queue = queue.Queue()
        self._response_events = {}
        self._transformer_task = []
        self._processor_region = []
        self._transformed = 0

        for task in self.batch_tasks:
            self._queue.put(task)

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
    def system_shutdown(self):
        with self.lock:
            return self._system_shutdown

    @system_shutdown.setter
    def system_shutdown(self, value):
        with self.lock:
            self._system_shutdown = value

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
    def processor_region(self):
        with self.lock:
            return self._processor_region

    @processor_region.setter
    def processor_region(self, value):
        with self.lock:
            self._processor_region = value

    def is_region_available(self, region):
        with self.lock:
            return region in self._processor_region

    @property
    def transformed(self):
        with self.lock:
            return self._transformed

    @transformed.setter
    def transformed(self, value):
        with self.lock:
            self._transformed = value

    @property
    def queue(self):
        with self.lock:
            return self._queue

    def put_task(self, task):
        with self.lock:
            self._queue.put(task)

    def get_task(self):
        with self.lock:
            if not self._queue.empty():
                return self._queue.get()
            else:
                return None

    def requeue_task(self, task):
        with self.lock:
            self._queue.put(task)

    def task_done(self):
        with self.lock:
            self._queue.task_done()


# Create a singleton instance of the Config class
config = Config()
