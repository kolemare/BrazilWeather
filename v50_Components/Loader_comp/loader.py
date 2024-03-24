import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import os
import tempfile
from hdfs import InsecureClient
from comm import Comm


class Loader:
    def __init__(self, hdfs_host, hdfs_port, hdfs_user):
        self.hdfs_client = InsecureClient(f"{hdfs_host}:{hdfs_port}", user=hdfs_user)
        self.columns = ['date', 'hour', 'prcp', 'stp', 'smax', 'smin', 'gbrd',
                        'temp', 'dewp', 'tmax', 'tmin', 'dmax', 'dmin',
                        'hmax', 'hmin', 'hmdy', 'wdct', 'gust', 'wdsp', 'regi',
                        'prov', 'wsnm', 'inme', 'lat', 'lon', 'elvt']
        self.dtypes = {
            'date': str,
            'hour': str,
            'prcp': float,
            'stp': float,
            'smax': float,
            'smin': float,
            'gbrd': float,
            'temp': float,
            'dewp': float,
            'tmax': float,
            'tmin': float,
            'dmax': float,
            'dmin': float,
            'hmax': float,
            'hmin': float,
            'hmdy': float,
            'wdct': float,
            'gust': float,
            'wdsp': float,
            'regi': str,
            'prov': str,
            'wsnm': str,
            'inme': str,
            'lat': float,
            'lon': float,
            'elvt': float
        }

    def process_load_request(self, item):
        csv_file = f'dataset/{item}.csv'
        if os.path.exists(csv_file):
            with tempfile.TemporaryDirectory() as temp_dir:
                parquet_file = os.path.join(temp_dir, f"{item}.parquet")
                self.csv_to_parquet(csv_file, parquet_file)
                hdfs_path = f"/datalake/transformed/{item}.parquet"
                self.upload_to_hdfs_webhdfs(parquet_file, hdfs_path)
                return f"load:{item}:success"
        return f"load:{item}:failure"

    def csv_to_parquet(self, csv_file, parquet_file):
        df = pd.read_csv(csv_file, names=self.columns, dtype=self.dtypes, skiprows=1)
        df['prcp'] = df['prcp'].fillna(0)
        table = pa.Table.from_pandas(df)
        pq.write_table(table, parquet_file)

    def upload_to_hdfs_webhdfs(self, local_path, hdfs_path):
        with open(local_path, 'rb') as local_file:
            self.hdfs_client.write(hdfs_path, local_file, overwrite=True)

    def handle_request(self, payload):
        if payload.startswith("load:"):
            item = payload.split(":")[1]
            return self.process_load_request(item)
        elif payload == "shutdown":
            return "shutdown"


def main():
    loader = Loader('http://hadoop-container', 9870, 'root')
    comm = Comm("mqtt-broker", "loader", "responses")

    comm.start(loader.handle_request)

    # Keep the script running until shutdown request is received
    while True:
        # Add any additional logic here
        pass


if __name__ == "__main__":
    main()
