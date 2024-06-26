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
        self._alive_ping = (json_config['alive_ping'])
        self._hadoop_boot = json_config['hadoop_boot']
        self._port = json_config['port']
        self.batch_tasks = json_config['batch_tasks']
        self.realtime_tasks = json_config['realtime_tasks']
        self.sleep_duration = int(json_config['default_sleep'])
        self.shutdown_components = json_config['shutdown_components']

        # Global variables
        self._hadoop_status = False
        self._hadoop_services = False
        self._loader_status = False
        self._transformer_status = False
        self._processor_status = False
        self._realtime_status = False
        self._realtime_running = False
        self._system_shutdown = False
        self._realtime_configuration = False
        self._queue = deque()
        self._response_events = {}
        self._loader_completed = []
        self._transformer_task = []
        self._processor_region = []
        self._processed_tasks = []
        self._task_clusters = []
        self._ui_requests = []
        self._transformed = 0

        # Sort the batch_tasks by region
        sorted_tasks = sorted(self.batch_tasks, key=lambda x: x.get('region'))
        for task in sorted_tasks:
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
    def sleep_duration(self):
        with self.lock:
            return self._sleep_duration

    @sleep_duration.setter
    def sleep_duration(self, value):
        with self.lock:
            self._sleep_duration = value

    @property
    def hadoop_services(self):
        with self.lock:
            return self._hadoop_services

    @hadoop_services.setter
    def hadoop_services(self, value):
        with self.lock:
            self._hadoop_services = value

    @property
    def alive_ping(self):
        with self.lock:
            return self._alive_ping

    @alive_ping.setter
    def alive_ping(self, value):
        with self.lock:
            self._alive_ping = value

    @property
    def loader_status(self):
        with self.lock:
            return self._loader_status

    @loader_status.setter
    def loader_status(self, value):
        with self.lock:
            self._loader_status = value

    @property
    def transformer_status(self):
        with self.lock:
            return self._transformer_status

    @transformer_status.setter
    def transformer_status(self, value):
        with self.lock:
            self._transformer_status = value

    @property
    def processor_status(self):
        with self.lock:
            return self._processor_status

    @processor_status.setter
    def processor_status(self, value):
        with self.lock:
            self._processor_status = value

    @property
    def realtime_status(self):
        with self.lock:
            return self._realtime_status

    @realtime_status.setter
    def realtime_status(self, value):
        with self.lock:
            self._realtime_status = value

    @property
    def realtime_running(self):
        with self.lock:
            return self._realtime_running

    @realtime_running.setter
    def realtime_running(self, value):
        with self.lock:
            self._realtime_running = value

    @property
    def realtime_configuration(self):
        with self.lock:
            return self._realtime_configuration

    @realtime_configuration.setter
    def realtime_configuration(self, value):
        with self.lock:
            self._realtime_configuration = value

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
    def loader_completed(self):
        with self.lock:
            return self._loader_completed

    @loader_completed.setter
    def loader_completed(self, value):
        with self.lock:
            self._loader_completed = value

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
    def task_clusters(self):
        with self.lock:
            return self._task_clusters

    @task_clusters.setter
    def task_clusters(self, value):
        with self.lock:
            self._task_clusters = value

    @property
    def ui_requests(self):
        with self.lock:
            return self._ui_requests

    @ui_requests.setter
    def ui_requests(self, value):
        with self.lock:
            self._ui_requests = value

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

    def prioritize_task(self, task, all_regions=False):
        with self.lock:
            if not all_regions:
                self._ui_requests.append(task)
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
                        item.period >= task.period):
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
