import paho.mqtt.client as mqtt
import threading
import time
import uuid
from runtime import runtime, Task


def send_request_and_wait(client, request_topic, request_message, timeout=10):
    request_id = str(uuid.uuid4())
    event = threading.Event()
    runtime.response_events[request_id] = {'event': event, 'response': None}

    client.publish(request_topic, f"{request_id}:{request_message}")
    write_output(f"Marshaller: Sent request to {request_topic}: {request_message}")

    event.wait(timeout)

    response = runtime.response_events[request_id]['response']
    del runtime.response_events[request_id]

    return response


def on_message(client, userdata, message):
    topic = message.topic
    payload = str(message.payload.decode('utf-8'))
    if "response" == topic:
        request_id, response_message = payload.split(':', 1)
        write_output(f"Marshaller: Received response on topic {topic}: {response_message}")

        if request_id in runtime.response_events:
            runtime.response_events[request_id]['response'] = response_message
            runtime.response_events[request_id]['event'].set()

    elif "marshaller" == topic:
        handle_ui(client, payload)

    elif "info" == topic:
        write_output(payload)

    else:
        write_output(f"Marshaller: Unknown topic: {payload}")


def start_hdfs(client):
    while not runtime.hadoop_status:
        response = send_request_and_wait(client, "hdfs", "hdfs:start", runtime.hadoop_boot)
        if response == "hdfs:start:success":
            runtime.hadoop_status = True
            write_output("Marshaller: Successfully started HDFS!")
        elif response == "hdfs:start:failure":
            write_output("Marshaller: Trying to start HDFS again!")
        else:
            raise Exception("Marshaller: Timeout while starting HDFS services.")


def handle_loader(client):
    for item in runtime.data:
        while True:
            time.sleep(5)
            if not runtime.hadoop_status:
                continue
            response = send_request_and_wait(client, "loader", f"load:{item}", runtime.time_threshold)
            if response is not None:
                if response == f"load:{item}:success":
                    write_output(f"Marshaller: Success for loading: {item}")
                    runtime.transformer_task.append(item)
                    break
                elif response == f"load:{item}:failure":
                    write_output(f"Marshaller: Failed Re-requesting loading of: {item}")
                else:
                    write_output(f"Marshaller: Unknown error (loader)")
            else:
                write_output("Marshaller: Timeout for load request.")
                raise Exception("Timeout for load request")
    return shut_down_component(client, "loader")


def handle_transformer(client):
    while True:

        time.sleep(5)

        if runtime.transformed == len(runtime.data):
            return shut_down_component(client, "transformer")

        if not runtime.hadoop_status:
            continue

        for item in runtime.transformer_task:
            response = send_request_and_wait(client, "transformer", f"transform:{item}", runtime.time_threshold)
            if response is not None:
                if response == f"transform:{item}:success":
                    write_output(f"Marshaller: Success for transforming: {item}")
                    runtime.transformer_task.remove(item)
                    runtime.processor_region.append(item)
                    runtime.transformed += 1
                    break
                elif response == f"transform:{item}:failure":
                    write_output(f"Marshaller: Failed Re-requesting transforming of: {item}")
                else:
                    write_output(f"Marshaller: Unknown error (transformer)")
            else:
                write_output("Marshaller: Timeout for transform request.")
                raise Exception("Timeout for transform request")


def handle_processor(client):
    while not runtime.system_shutdown:
        time.sleep(3)
        if not runtime.hadoop_status:
            continue

        for group in runtime.task_clusters:
            task_group_processed = True
            temp_task = None
            for single in group:
                temp_task = single
                if not runtime.task_has_been_processed(single):
                    task_group_processed = False
            if task_group_processed:
                write_output("Marshaller: Task cluster processed")
                write_output(f"UI: Request for all regions {temp_task.operation} for duration {temp_task.period} is ready.")
                client.publish("ui", f"marshaller:all:{temp_task.operation}:{temp_task.period}:success")
                runtime.task_clusters.remove(group)

        task = runtime.get_task()

        if task is None:
            write_output("Processor: No tasks in queue")
            continue

        if runtime.task_has_been_processed(task):
            write_output("Marshaller: Requested task has already been processed!")
            if runtime.ui_has_requested_task(task):
                write_output(f"UI: Request for region: {task.region}, calculation: {task.operation} for duration {task.period} is ready.")
                client.publish("ui", f"marshaller:{task.region}:{task.operation}:{task.period}:success")
            continue

        # Check if the region is available (already transformed in curated zone)
        if not runtime.is_region_available(task.region):
            # Re-queue the task with low priority
            runtime.put_task(task, priority=False)
            write_output(f"Marshaller: Region {task.region} is not available for processing, re-queueing task.")
            continue

        response = send_request_and_wait(client, "processor", f"{task.operation}:{task.region}:{task.period}",
                                         runtime.time_threshold)
        if response is not None:
            if response == f"{task.operation}:{task.region}:{task.period}:success":
                write_output(
                    f"Marshaller: Success for calculating {task.operation} for {task.region}, period: {task.period}")
                runtime.processed_tasks.append(task)
                if runtime.ui_has_requested_task(task):
                    write_output(f"UI: Request for region: {task.region}, calculation: {task.operation} for duration {task.period} is ready.")
                    client.publish("ui", f"marshaller:{task.region}:{task.operation}:{task.period}:success")
            elif response == f"{task.operation}:{task.region}:{task.period}:failure":
                write_output(f"Marshaller: Failed Re-requesting calculation of {task.operation} for {task.region}")
            else:
                write_output(f"Marshaller: Unknown error (processor)")
        else:
            write_output("Marshaller: Timeout for processor request.")
            raise Exception("Timeout for processor request")
    return shut_down_component(client, "processor")


def handle_ui(client, payload):
    parts = payload.split(":")
    if len(parts) != 3:
        client.publish("ui", "invalid")
    region, command, period = parts
    if command == "shutdown":
        runtime.system_shutdown = True
        for item in runtime.shutdown_components:
            shut_down_component(client, item)
    else:
        write_output(f"UI: Has requested {command} for region: {region} for period {period}")
        if "all" == region:
            task_group = []
            for item in runtime.data:
                runtime.prioritize_task(Task(item, command, int(period)), all_regions=True)
                task_group.append(Task(item, command, int(period)))
            runtime.task_clusters.append(task_group)
        else:
            runtime.prioritize_task(Task(region, command, int(period)), all_regions=False)


def shut_down_component(client, component):
    while True:
        response = send_request_and_wait(client, component, f"shutdown:{None}", runtime.time_threshold)
        if response is not None:
            if response == f"{component}:shutdown:acknowledged":
                return
            else:
                write_output(f"Marshaller: Re-requesting shutdown of {component}.")
        else:
            write_output(f"Marshaller: Timeout for shutting down {component}.")
            raise Exception(f"Timeout for shutting down {component}.")


def write_output(message):
    color_codes = {
        "HDFS": '\033[97m',  # White
        "Processor": '\033[94m',  # Blue
        "UI": '\033[92m',  # Green
        "Loader": '\033[93m',  # Yellow
        "Transformer": '\033[96m',  # Cyan
        "Database": '\033[95m',  # Purple
        "Marshaller": '\033[90m',  # Black
        "Runtime": '\033[91m'  # Red
    }

    reset_code = '\033[0m'
    prefix = message.split(':')[0]

    color_code = color_codes.get(prefix, reset_code)
    colored_message = f"{color_code}{message}{reset_code}"

    print(colored_message)


def main():
    port = runtime.port
    client = mqtt.Client("marshaller")
    client.on_message = lambda client, userdata, message: on_message(client, userdata, message)
    client.connect("mqtt-broker", port)
    client.subscribe("marshaller")
    client.subscribe("response")
    client.subscribe("info")
    client.loop_start()

    start_hdfs_thread = threading.Thread(target=start_hdfs, args=(client,))
    transformer_thread = threading.Thread(target=handle_transformer, args=(client,))
    processor_thread = threading.Thread(target=handle_processor, args=(client,))
    loader_thread = threading.Thread(target=handle_loader, args=(client,))

    start_hdfs_thread.start()
    transformer_thread.start()
    processor_thread.start()
    loader_thread.start()

    start_hdfs_thread.join()
    transformer_thread.join()
    processor_thread.join()
    loader_thread.join()

    client.loop_stop()


if __name__ == "__main__":
    main()
