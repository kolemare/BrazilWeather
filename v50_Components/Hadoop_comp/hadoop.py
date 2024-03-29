from comm import Comm
import subprocess
import threading
import time


class Hadoop:
    def __init__(self, broker_address, request_topic, response_topic):
        self.comm = Comm(broker_address, request_topic, response_topic)
        self.shutdown_event = threading.Event()

    def handle_request(self, payload):
        request_id, message = payload.split(':', 1)
        self.comm.send_info(message)
        if message == "hdfs:start":
            subprocess.run(["/usr/local/startHadoopServices.sh"])
            # Check if HDFS NameNode and DataNode are running
            namenode_status = subprocess.run(["jps"], capture_output=True, text=True).stdout.find("NameNode") != -1
            datanode_status = subprocess.run(["jps"], capture_output=True, text=True).stdout.find("DataNode") != -1
            if namenode_status and datanode_status:
                self.comm.send_info("HDFS service running...")
                return f"{request_id}:hdfs:start:success"
            else:
                self.comm.send_info("HDFS service starting failure...")
                return f"{request_id}:hdfs:start:failure"
        elif message == "hdfs:stop":
            subprocess.run(["/usr/local/stopHadoopServices.sh"])
            # Check if HDFS NameNode and DataNode are stopped
            namenode_status = subprocess.run(["jps"], capture_output=True, text=True).stdout.find("NameNode") == -1
            datanode_status = subprocess.run(["jps"], capture_output=True, text=True).stdout.find("DataNode") == -1
            if namenode_status and datanode_status:
                self.comm.send_info("HDFS service stopped.")
                return f"{request_id}:hdfs:stop:success"
            else:
                self.comm.send_info("HDFS service stopping failure...")
                return f"{request_id}:hdfs:stop:failure"
        elif message == "alive:request":
            self.comm.send_info("Alive => Running...")
            return f"{request_id}:hdfs:alive:waiting"
        elif message == f"shutdown:{None}":
            self.comm.send_info("Received shutdown command!")
            self.shutdown_event.set()
            return f"{request_id}:hdfs:shutdown:acknowledged"

    def start(self):
        self.comm.start(self.handle_request)

    def stop(self):
        self.comm.stop()

    def run(self):
        self.start()
        self.shutdown_event.wait()
        self.comm.send_info("Shutting down communication...")
        self.comm.send_info("Shutting down...")
        self.stop()


if __name__ == "__main__":
    hadoop = Hadoop("mqtt-broker", "hdfs", "response")
    hadoop.run()
