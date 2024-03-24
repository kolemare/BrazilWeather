from comm import Comm
import subprocess
import time

def handle_request(payload):
    request_id, message = payload.split(':', 1)
    if message == "hdfs:start":
        subprocess.run(["/usr/local/startHadoopServices.sh"])
        # Check if HDFS NameNode and DataNode are running
        namenode_status = subprocess.run(["jps"], capture_output=True, text=True).stdout.find("NameNode") != -1
        datanode_status = subprocess.run(["jps"], capture_output=True, text=True).stdout.find("DataNode") != -1
        if namenode_status and datanode_status:
            return f"{request_id}:hdfs:start:success"
        else:
            return f"{request_id}:hdfs:start:failure"
    elif message == "hdfs:stop":
        subprocess.run(["/usr/local/stopHadoopServices.sh"])
        # Check if HDFS NameNode and DataNode are stopped
        namenode_status = subprocess.run(["jps"], capture_output=True, text=True).stdout.find("NameNode") == -1
        datanode_status = subprocess.run(["jps"], capture_output=True, text=True).stdout.find("DataNode") == -1
        if namenode_status and datanode_status:
            return f"{request_id}:hdfs:stop:success"
        else:
            return f"{request_id}:hdfs:stop:failure"

def main():
    comm = Comm("mqtt-broker", "hdfs", "response")
    comm.start(handle_request)

    # Keep the script running
    while True:
        time.sleep(5)
        pass

if __name__ == "__main__":
    main()