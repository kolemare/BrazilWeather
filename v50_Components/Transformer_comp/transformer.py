import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import os
import numpy as np
from hdfs import InsecureClient

# HDFS configuration
hdfs_host = 'http://hadoop-container'  # WebHDFS endpoint
hdfs_port = 9870
hdfs_user = 'root'

# Create a WebHDFS client
client = InsecureClient(f"{hdfs_host}:{hdfs_port}", user=hdfs_user)

def read_parquet_from_hdfs(client, hdfs_path):
    with client.read(hdfs_path) as reader:
        data = reader.read()
        return pq.read_table(pa.BufferReader(data)).to_pandas()

def clean_data(df):
    for column in df.columns:
        # Replace -9999 with NaN and remove them from calculation
        df[column].replace(-9999, np.nan, inplace=True)
    df.dropna(inplace=True)
    return df

def write_parquet_to_hdfs(client, df, hdfs_path):
    buffer = pa.BufferOutputStream()
    pq.write_table(pa.Table.from_pandas(df), buffer)
    with client.write(hdfs_path, overwrite=True) as writer:
        writer.write(buffer.getvalue())

# Paths to your Parquet files in HDFS
hdfs_paths = [
    '/datalake/transformed/central_west.parquet',
    '/datalake/transformed/north.parquet',
    '/datalake/transformed/northeast.parquet',
    '/datalake/transformed/south.parquet',
    '/datalake/transformed/southeast.parquet'
]

for path in hdfs_paths:
    region = os.path.basename(path).split('.')[0]
    print(f"Cleaning data for {region}...")
    df = read_parquet_from_hdfs(client, path)
    cleaned_df = clean_data(df)
    # Define the output path in the 'datalake/curated' directory
    output_path = f'/datalake/curated/{region}.parquet'
    write_parquet_to_hdfs(client, cleaned_df, output_path)
    print(f"Cleaned data for {region} uploaded to HDFS at {output_path}")