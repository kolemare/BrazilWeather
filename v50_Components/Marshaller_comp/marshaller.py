import paho.mqtt.client as mqtt
import threading
import time
import uuid
from configuration import config


def send_request_and_wait(client, request_topic, request_message, timeout=10):
    request_id = str(uuid.uuid4())
    event = threading.Event()
    config.response_events[request_id] = {'event': event, 'response': None}

    client.publish(request_topic, f"{request_id}:{request_message}")
    write_output(f"Marshaller: Sent request to {request_topic}: {request_message}")

    event.wait(timeout)

    response = config.response_events[request_id]['response']
    del config.response_events[request_id]

    return response


def on_message(client, userdata, message):
    topic = message.topic
    payload = str(message.payload.decode('utf-8'))
    if "response" == topic:
        request_id, response_message = payload.split(':', 1)
        write_output(f"Marshaller: Received response on topic {topic}: {response_message}")

        if request_id in config.response_events:
            config.response_events[request_id]['response'] = response_message
            config.response_events[request_id]['event'].set()

    elif "info" == topic:
        write_output(payload)

    else:
        write_output(f"Marshaller: Unknown topic: {payload}")


def start_hdfs(client):
    while not config.hadoop_status:
        response = send_request_and_wait(client, "hdfs", "hdfs:start", config.hadoop_boot)
        if response == "hdfs:start:success":
            config.hadoop_status = True
            write_output("Marshaller: Successfully started HDFS!")
        elif response == "hdfs:start:failure":
            write_output("Marshaller: Trying to start HDFS again!")
        else:
            raise Exception("Marshaller: Timeout while starting HDFS services.")


def handle_loader(client):
    for item in config.data:
        while True:
            time.sleep(5)
            if not config.hadoop_status:
                continue
            response = send_request_and_wait(client, "loader", f"load:{item}", config.time_threshold)
            if response is not None:
                if response == f"load:{item}:success":
                    write_output(f"Marshaller: Success for loading: {item}")
                    config.transformer_task.append(item)
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

        if config.transformed == len(config.data):
            return shut_down_component(client, "transformer")

        if not config.hadoop_status:
            continue

        for item in config.transformer_task:
            response = send_request_and_wait(client, "transformer", f"transform:{item}", config.time_threshold)
            if response is not None:
                if response == f"transform:{item}:success":
                    write_output(f"Marshaller: Success for transforming: {item}")
                    config.transformer_task.remove(item)
                    config.processor_region.append(item)
                    config.transformed += 1
                    break
                elif response == f"transform:{item}:failure":
                    write_output(f"Marshaller: Failed Re-requesting transforming of: {item}")
                else:
                    write_output(f"Marshaller: Unknown error (transformer)")
            else:
                write_output("Marshaller: Timeout for transform request.")
                raise Exception("Timeout for transform request")


def handle_processor(client):
    while not config.system_shutdown:
        time.sleep(5)
        if not config.hadoop_status:
            continue

        task = config.get_task()

        if task is None:
            continue

        # Extract task details
        operation = task.get('operation')
        region = task.get('region')
        period = int(task.get('period'))

        # Check if the region is available (already transformed in curated zone)
        if not config.is_region_available(region):
            # Re-queue the task and continue with the next iteration
            config.requeue_task(task)
            write_output(f"Marshaller: Region {region} is not available for processing, re-queueing task.")
            continue

        response = send_request_and_wait(client, "processor", f"{operation}:{region}:{period}", config.time_threshold)
        if response is not None:
            if response == f"{operation}:{region}:{period}:success":
                write_output(f"Marshaller: Success for calculating {operation} for {region}")
            elif response == f"{operation}:{region}:{period}:failure":
                write_output(f"Marshaller: Failed Re-requesting calculation of {operation} for {region}")
            else:
                write_output(f"Marshaller: Unknown error (processor)")
        else:
            write_output("Marshaller: Timeout for processor request.")
            raise Exception("Timeout for processor request")

        # Mark the task as done
        config.task_done()
    return shut_down_component(client, "processor")


def shut_down_component(client, component):
    while True:
        response = send_request_and_wait(client, component, f"shutdown:{None}", config.time_threshold)
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
    port = config.port
    client = mqtt.Client("marshaller")
    client.on_message = lambda client, userdata, message: on_message(client, userdata, message)
    client.connect("mqtt-broker", port)
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
