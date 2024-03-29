import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import os
import tempfile
from hdfs import InsecureClient
from comm import Comm
import time
import threading


class Loader:
    def __init__(self, hdfs_host, hdfs_port, hdfs_user):
        self.hdfs_client = InsecureClient(f"{hdfs_host}:{hdfs_port}", user=hdfs_user)
        self.columns = [
            'date', 'hour', 'prcp', 'stp', 'smax', 'smin', 'gbrd',
            'temp', 'dewp', 'tmax', 'tmin', 'dmax', 'dmin',
            'hmax', 'hmin', 'hmdy', 'wdct', 'gust', 'wdsp', 'regi',
            'prov', 'wsnm', 'inme', 'lat', 'lon', 'elvt'
        ]
        self.dtypes = {
            'date': str, 'hour': str, 'prcp': float, 'stp': float, 'smax': float,
            'smin': float, 'gbrd': float, 'temp': float, 'dewp': float, 'tmax': float,
            'tmin': float, 'dmax': float, 'dmin': float, 'hmax': float, 'hmin': float,
            'hmdy': float, 'wdct': float, 'gust': float, 'wdsp': float, 'regi': str,
            'prov': str, 'wsnm': str, 'inme': str, 'lat': float, 'lon': float, 'elvt': float
        }
        self.shutdown_event = threading.Event()

    def process_load_request(self, item, comm):
        csv_file = f'dataset/{item}.csv'
        if os.path.exists(csv_file):
            with tempfile.TemporaryDirectory() as temp_dir:
                parquet_file = os.path.join(temp_dir, f"{item}.parquet")
                comm.send_info(f"Wrapping {item} to parquet format...")
                self.csv_to_parquet(csv_file, parquet_file)
                hdfs_path = f"/datalake/transformed/{item}.parquet"
                comm.send_info(f"Uploading {item} to HDFS...")
                self.upload_to_hdfs_webhdfs(parquet_file, hdfs_path)
                return "success"
        comm.send_info(f"Uploading of {item} to HDFS failed.")
        return "failure"

    def csv_to_parquet(self, csv_file, parquet_file):
        df = pd.read_csv(csv_file, names=self.columns, dtype=self.dtypes, skiprows=1)
        df['prcp'] = df['prcp'].fillna(0)
        table = pa.Table.from_pandas(df)
        pq.write_table(table, parquet_file)

    def upload_to_hdfs_webhdfs(self, local_path, hdfs_path):
        with open(local_path, 'rb') as local_file:
            self.hdfs_client.write(hdfs_path, local_file, overwrite=True)

    def handle_request(self, payload, comm):
        parts = payload.split(":")
        if len(parts) != 3:
            comm.send_info("Invalid message format received.")
            return "command:invalid"
        request_id, command, item = parts
        if command == "load":
            comm.send_info(f"Received request to load {item}")
            result = self.process_load_request(item, comm)
            return f"{request_id}:{command}:{item}:{result}"
        elif command == "shutdown":
            comm.send_info("Received shutdown command!")
            self.shutdown_event.set()
            return f"{request_id}:loader:{command}:acknowledged"
        else:
            comm.send_info(f"Unknown command: {command}")
            return f"{request_id}:{command}:{item}:error"


def main():
    loader = Loader('http://hadoop-container', 9870, 'root')
    comm = Comm("mqtt-broker", "loader", "response")

    comm.start(loader.handle_request)
    loader.shutdown_event.wait()
    comm.send_info("Shutting down communication...")
    comm.send_info("Shutting down...")
    comm.stop()


if __name__ == "__main__":
    main()
