import time
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import os
import numpy as np
from hdfs import InsecureClient
from comm import Comm


class Transformer:
    def __init__(self, hdfs_host, hdfs_port, hdfs_user):
        self.hdfs_client = InsecureClient(f"{hdfs_host}:{hdfs_port}", user=hdfs_user)

    def read_parquet_from_hdfs(self, hdfs_path):
        with self.hdfs_client.read(hdfs_path) as reader:
            data = reader.read()
            return pq.read_table(pa.BufferReader(data)).to_pandas()

    @staticmethod
    def clean_data(df):
        for column in df.columns:
            df[column].replace(-9999, np.nan, inplace=True)
        df.dropna(inplace=True)
        return df

    def write_parquet_to_hdfs(self, df, hdfs_path):
        buffer = pa.BufferOutputStream()
        pq.write_table(pa.Table.from_pandas(df), buffer)
        with self.hdfs_client.write(hdfs_path, overwrite=True) as writer:
            writer.write(buffer.getvalue())

    def handle_request(self, payload):
        parts = payload.split(":")
        if len(parts) != 3:
            print("Invalid message format received.")
            return "command:invalid"
        request_id, command, region = parts
        if command == "transform":
            try:
                path = f'/datalake/transformed/{region}.parquet'
                print(f"Cleaning data for {region}...")
                df = self.read_parquet_from_hdfs(path)
                cleaned_df = self.clean_data(df)
                output_path = f'/datalake/curated/{region}.parquet'
                self.write_parquet_to_hdfs(cleaned_df, output_path)
                print(f"Cleaned data for {region} uploaded to HDFS at {output_path}")
                return f"{request_id}:{command}:success"
            except Exception as e:
                print(f"Error transforming data for {region}: {e}")
                return f"{request_id}:{command}:failure"
        else:
            print(f"Unknown command: {command}")
            return f"{request_id}:{command}:error"


def main():
    transformer = Transformer('http://hadoop-container', 9870, 'root')
    comm = Comm("mqtt-broker", "transformer", "response")

    comm.start(transformer.handle_request)

    # Keep the script running until a shutdown request is received
    while True:
        time.sleep(5)
        pass


if __name__ == "__main__":
    main()
