import paho.mqtt.client as mqtt
import threading
import time
import json
import uuid


def send_request_and_wait(client, request_topic, request_message, timeout=10):
    request_id = str(uuid.uuid4())
    event = threading.Event()
    response_events[request_id] = {'event': event, 'response': None}

    client.publish(request_topic, f"{request_id}:{request_message}")
    write_output(f"Marshaller: Sent request to {request_topic}: {request_message} with ID: {request_id}")

    event.wait(timeout)

    response = response_events[request_id]['response']
    del response_events[request_id]

    return response

def on_message(client, userdata, message):
    topic = message.topic
    payload = str(message.payload.decode('utf-8'))
    request_id, response_message = payload.split(':', 1)
    write_output(f"Marshaller: Received response on topic {topic}: {response_message} for ID: {request_id}")

    if request_id in response_events:
        response_events[request_id]['response'] = response_message
        response_events[request_id]['event'].set()


def start_hdfs(client, time_threshold):
    global hadoop_status
    while not hadoop_status:
        response = send_request_and_wait(client, "hdfs", "hdfs:start", time_threshold)
        if response == "hdfs:start:success":
            hadoop_status = True
            write_output("Marshaller:Successfully started hdfs!")
        elif response == "hdfs:start:failure":
            write_output("Marshaller:Trying to start hdfs again!")
        else:
            raise Exception("Timeout while starting hadoop services.")


def handle_loader(client, configuration, time_threshold):
    for item in configuration:
        while True:
            time.sleep(5)
            if not hadoop_status:
                continue
            response = send_request_and_wait(client, "loader", f"load:{item}", time_threshold)
            write_output(f"Marshaller: Sent request to loader to load: {item}")

            if response is not None:
                if response == f"load:{item}:success":
                    write_output(f"Marshaller: Success for loading: {item}")
                    break
                else:
                    write_output(f"Marshaller: Re-requesting loading of: {item}")
            else:
                raise Exception


def handle_transformer(client, configuration):
    for item in configuration:
        while True:
            time.sleep(5)
            response = send_request_and_wait(client, "transformer", f"transform:{item}")
            write_output(f"Marshaller: Sent request to transformer to transform: {item}")

            if response is not None:
                if response == f"transform:{item}:success":
                    write_output(f"Marshaller: Success for transforming: {item}")
                    break
                else:
                    write_output(f"Marshaller: Re-requesting transformation of: {item}")
            else:
                raise Exception


def write_output(message):
    print(message)


def main():
    global response_events
    response_events = {}

    global hadoop_status
    hadoop_status = False

    with open('configuration.json', 'r') as file:
        json_config = json.load(file)
    configuration = json_config['data']
    time_threshold = json_config['max_wait_time']
    hadoop_boot = json_config['hadoop_boot']

    port = 1883
    client = mqtt.Client("marshaller")
    client.on_message = lambda client, userdata, message: on_message(client, userdata, message)
    client.connect("mqtt-broker", port)
    client.subscribe("response")
    client.loop_start()

    start_hdfs_thread = threading.Thread(target=start_hdfs, args=(client, hadoop_boot,))
    #transformer_thread = threading.Thread(target=handle_transformer, args=(client, configuration,))
    loader_thread = threading.Thread(target=handle_loader, args=(client, configuration, time_threshold,))

    start_hdfs_thread.start()
    #transformer_thread.start()
    loader_thread.start()

    start_hdfs_thread.join()
    #transformer_thread.join()
    loader_thread.join()

    client.loop_stop()


if __name__ == "__main__":
    main()
