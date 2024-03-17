import sqlite3
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import pyarrow.fs
import numpy as np
import os
from datetime import datetime

# HDFS Configuration
hdfs_host = 'localhost'
hdfs_port = 9000
hadoop_fs = pyarrow.fs.HadoopFileSystem(hdfs_host, hdfs_port)

def read_parquet_from_hdfs(hadoop_fs, hdfs_path):
    with hadoop_fs.open_input_file(hdfs_path) as f:
        return pq.read_table(f).to_pandas()

def calculate_avg_temp_per_month(df):
    # Replace -9999 with NaN and remove them from calculation
    df['temp'].replace(-9999, np.nan, inplace=True)
    df.dropna(subset=['temp'], inplace=True)

    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
    df['month'] = df['date'].dt.month
    return df.groupby('month')['temp'].mean().reset_index(name='avg_temp')

# Paths to your Parquet files in HDFS
hdfs_paths = [
    '/datalake/central_west/central_west.parquet',
    '/datalake/north/north.parquet',
    '/datalake/northeast/northeast.parquet',
    '/datalake/south/south.parquet',
    '/datalake/southeast/southeast.parquet'
]

# SQLite Configuration
sqlite_db_path = 'weather_data.db'
conn = sqlite3.connect(sqlite_db_path)
cursor = conn.cursor()

# Create table for average temperatures
cursor.execute('''
    CREATE TABLE IF NOT EXISTS avg_temp_per_month (
        region TEXT,
        month INTEGER,
        avg_temp REAL
    )
''')

for path in hdfs_paths:
    region = os.path.basename(path).split('.')[0]
    print(f"Processing data for {region}...")
    df = read_parquet_from_hdfs(hadoop_fs, path)
    avg_temp_df = calculate_avg_temp_per_month(df)
    avg_temp_df['region'] = region
    # Correct the renaming of columns
    avg_temp_df.columns = ['month', 'avg_temp', 'region']
    avg_temp_df.to_sql('avg_temp_per_month', conn, if_exists='append', index=False)

conn.close()
print("Data processing and storage completed.")