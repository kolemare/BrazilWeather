import paho.mqtt.client as mqtt
import threading
import time
import uuid
from runtime import Runtime, Task
from comm import Comm
from logger import Logger


class Marshaller:
    def __init__(self, instance, broker_address):
        self.shutdown_event = threading.Event()
        self.broker_address = broker_address
        self.comm = Comm(instance, broker_address, ["marshaller", "response"])
        self.runtime = Runtime()

    def send_request_and_wait(self, request_topic, request_message, timeout=10):
        request_id = str(uuid.uuid4())
        event = threading.Event()
        self.runtime.response_events[request_id] = {'event': event, 'response': None}

        self.comm.client.publish(request_topic, f"{request_id}:{request_message}")
        self.comm.send_info(f"Sent request to {request_topic}: {request_message}")

        event.wait(timeout)

        response = self.runtime.response_events[request_id]['response']
        del self.runtime.response_events[request_id]

        return response

    def on_message(self, client, userdata, message):
        topic = message.topic
        payload = str(message.payload.decode('utf-8'))
        if "response" == topic:
            request_id, response_message = payload.split(':', 1)
            self.comm.send_info(f"Received response on topic {topic}: {response_message}")

            if request_id in self.runtime.response_events:
                self.runtime.response_events[request_id]['response'] = response_message
                self.runtime.response_events[request_id]['event'].set()

        elif "marshaller" == topic:
            self.handle_ui(payload)

        else:
            self.comm.send_info(f"Unknown topic: {payload}")

    def start_hdfs(self):
        while not self.runtime.hadoop_status:
            response = self.send_request_and_wait("hdfs", "hdfs:start", self.runtime.hadoop_boot)
            if response == "hdfs:start:success":
                self.runtime.hadoop_status = True
                self.comm.send_info("Successfully started HDFS!")
            elif response == "hdfs:start:failure":
                self.comm.send_info("Trying to start HDFS again!")
            else:
                raise Exception("Marshaller: Timeout while starting HDFS services.")

    def handle_loader(self):
        for item in self.runtime.data:
            while True:
                time.sleep(5)
                if not self.runtime.hadoop_status:
                    continue
                response = self.send_request_and_wait("loader", f"load:{item}", self.runtime.time_threshold)
                if response is not None:
                    if response == f"load:{item}:success":
                        self.comm.send_info(f"Success for loading: {item}")
                        self.runtime.transformer_task.append(item)
                        break
                    elif response == f"load:{item}:failure":
                        self.comm.send_info(f"Failed Re-requesting loading of: {item}")
                    else:
                        self.comm.send_info(f"Unknown error (loader)")
                else:
                    self.comm.send_info("Marshaller: Timeout for load request.")
                    raise Exception("Timeout for load request")
        return self.shut_down_component("loader")

    def handle_transformer(self):
        while True:

            time.sleep(5)

            if self.runtime.transformed == len(self.runtime.data):
                return self.shut_down_component("transformer")

            if not self.runtime.hadoop_status:
                continue

            for item in self.runtime.transformer_task:
                response = self.send_request_and_wait("transformer", f"transform:{item}", self.runtime.time_threshold)
                if response is not None:
                    if response == f"transform:{item}:success":
                        self.comm.send_info(f"Success for transforming: {item}")
                        self.runtime.transformer_task.remove(item)
                        self.runtime.processor_region.append(item)
                        self.runtime.transformed += 1
                        break
                    elif response == f"transform:{item}:failure":
                        self.comm.send_info(f"Failed Re-requesting transforming of: {item}")
                    else:
                        self.comm.send_info(f"Unknown error (transformer)")
                else:
                    self.comm.send_info("Timeout for transform request.")
                    raise Exception("Timeout for transform request")

    def handle_processor(self):
        while not self.runtime.system_shutdown:
            time.sleep(3)
            if not self.runtime.hadoop_status:
                continue

            for group in self.runtime.task_clusters:
                task_group_processed = True
                temp_task = None
                for single in group:
                    temp_task = single
                    if not self.runtime.task_has_been_processed(single):
                        task_group_processed = False
                if task_group_processed:
                    self.comm.send_info("Task cluster processed")
                    Logger.write_output(
                        f"UI: Request for all regions {temp_task.operation} for duration {temp_task.period} is ready.")
                    self.comm.client.publish("ui", f"marshaller:all:{temp_task.operation}:{temp_task.period}:success")
                    self.runtime.task_clusters.remove(group)

            task = self.runtime.get_task()

            if task is None:
                Logger.write_output("Processor: No tasks in queue")
                continue

            if self.runtime.task_has_been_processed(task):
                self.comm.send_info("Requested task has already been processed!")
                if self.runtime.ui_has_requested_task(task):
                    Logger.write_output(
                        f"UI: Request for region: {task.region}, calculation: {task.operation} for duration {task.period} is ready.")
                    self.comm.client.publish("ui", f"marshaller:{task.region}:{task.operation}:{task.period}:success")
                continue

            # Check if the region is available (already transformed in curated zone)
            if not self.runtime.is_region_available(task.region):
                # Re-queue the task with low priority
                self.runtime.put_task(task, priority=False)
                self.comm.send_info(f"Region {task.region} is not available for processing, re-queueing task.")
                continue

            response = self.send_request_and_wait("processor", f"{task.operation}:{task.region}:{task.period}",
                                                  self.runtime.time_threshold)
            if response is not None:
                if response == f"{task.operation}:{task.region}:{task.period}:success":
                    self.comm.send_info(
                        f"Success for calculating {task.operation} for {task.region}, period: {task.period}")
                    self.runtime.processed_tasks.append(task)
                    if self.runtime.ui_has_requested_task(task):
                        Logger.write_output(
                            f"UI: Request for region: {task.region}, calculation: {task.operation} for duration {task.period} is ready.")
                        self.comm.client.publish("ui",
                                                 f"marshaller:{task.region}:{task.operation}:{task.period}:success")
                elif response == f"{task.operation}:{task.region}:{task.period}:failure":
                    self.comm.send_info(f"Failed Re-requesting calculation of {task.operation} for {task.region}")
                else:
                    self.comm.send_info(f"Unknown error (processor)")
            else:
                self.comm.send_info("Timeout for processor request.")
                raise Exception("Timeout for processor request")
        return self.shut_down_component("processor")

    def handle_ui(self, payload):
        parts = payload.split(":")
        if len(parts) != 3:
            self.comm.client.publish("ui", "invalid")
        region, command, period = parts
        if command == "shutdown":
            self.runtime.system_shutdown = True
            for item in self.runtime.shutdown_components:
                self.shut_down_component(item)
        else:
            Logger.write_output(f"UI: Has requested {command} for region: {region} for period {period}")
            if "all" == region:
                task_group = []
                for item in self.runtime.data:
                    self.runtime.prioritize_task(Task(item, command, int(period)), all_regions=True)
                    task_group.append(Task(item, command, int(period)))
                self.runtime.task_clusters.append(task_group)
            else:
                self.runtime.prioritize_task(Task(region, command, int(period)), all_regions=False)

    def shut_down_component(self, component):
        while True:
            response = self.send_request_and_wait(component, f"shutdown:{None}", self.runtime.time_threshold)
            if response is not None:
                if response == f"{component}:shutdown:acknowledged":
                    return
                else:
                    self.comm.send_info(f"Re-requesting shutdown of {component}.")
            else:
                self.comm.send_info(f"Marshaller: Timeout for shutting down {component}.")
                raise Exception(f"Timeout for shutting down {component}.")

    def run(self):
        start_hdfs_thread = threading.Thread(target=self.start_hdfs, args=())
        transformer_thread = threading.Thread(target=self.handle_transformer, args=())
        processor_thread = threading.Thread(target=self.handle_processor, args=())
        loader_thread = threading.Thread(target=self.handle_loader, args=())

        start_hdfs_thread.start()
        transformer_thread.start()
        processor_thread.start()
        loader_thread.start()

        start_hdfs_thread.join()
        transformer_thread.join()
        processor_thread.join()
        loader_thread.join()

        self.comm.client.loop_stop()


def main():
    marshaller = Marshaller("marshaller", "mqtt-broker")
    logger = Logger("info", "mqtt-broker")

    marshaller.comm.start(marshaller.on_message)
    marshaller.comm.client.loop_start()

    logger_thread = threading.Thread(target=logger.run)
    logger_thread.start()

    marshaller.run()

    Logger.stop_logger()
    logger_thread.join()


if __name__ == "__main__":
    main()
