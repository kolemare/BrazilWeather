import json
import threading
from collections import deque


class Task:
    def __init__(self, region, operation, period):
        self.region = region
        self.operation = operation
        self.period = period


class Runtime:
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
        self.shutdown_components = json_config['shutdown_components']

        # Global variables
        self._hadoop_status = False
        self._system_shutdown = False
        self._queue = deque()
        self._response_events = {}
        self._transformer_task = []
        self._processor_region = []
        self._processed_tasks = []
        self._ui_requests = []
        self._transformed = 0

        for task in self.batch_tasks:
            self._queue.append(Task(task.get('region'), task.get('operation'), int(task.get('period'))))

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
    def processed_tasks(self):
        with self.lock:
            return self._processed_tasks

    @processed_tasks.setter
    def processed_tasks(self, value):
        with self.lock:
            self._processed_tasks = value

    @property
    def ui_requests(self):
        with self.lock:
            return self._ui_requests

    @ui_requests.setter
    def ui_requests(self, value):
        with self.lock:
            self.ui_requests = value

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

    def put_task(self, task, priority=False):
        with self.lock:
            if priority:
                self._queue.appendleft(task)
            else:
                self._queue.append(task)

    def get_task(self):
        with self.lock:
            if self._queue:
                return self._queue.popleft()
            else:
                return None

    def prioritize_task(self, task):
        with self.lock:
            self._ui_requests.append(Task)
            for idx, queued_task in enumerate(self._queue):
                if (queued_task.region == task.region and
                        queued_task.operation == task.operation and
                        queued_task.period == task.period):
                    # Remove the task from its current position
                    del self._queue[idx]
                    # Add the task to the front of the queue
                    self._queue.appendleft(task)
                    return True
            # If the task is not found, add it to the front of the queue
            self._queue.appendleft(task)
            return False

    def task_has_been_processed(self, task):
        with self.lock:
            for item in self._processed_tasks:
                if (item.region == task.region and
                        item.operation == task.operation and
                        item.period == task.period):
                    return True
            return False

    def ui_has_requested_task(self, task):
        with self.lock:
            for item in self._ui_requests:
                if (item.region == task.region and
                        item.operation == task.operation and
                        item.period == task.period):
                    self._ui_requests.remove(item)
                    return True
            return False


# Create a singleton instance of the Runtime class
runtime = Runtime()
