import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import os
import subprocess
import tempfile
import time

# Docker container name
docker_container_name = 'hadoop-container'

# Column abbreviations and data types
columns = ['date', 'hour', 'prcp', 'stp', 'smax', 'smin', 'gbrd', 'temp', 'dewp', 'tmax', 'tmin', 'dmax', 'dmin',
           'hmax', 'hmin', 'hmdy', 'wdct', 'gust', 'wdsp', 'regi', 'prov', 'wsnm', 'inme', 'lat', 'lon', 'elvt']
dtypes = {
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

# Function to run a command inside Docker
def run_in_docker(command):
    full_command = f"docker exec {docker_container_name} /bin/bash -c 'echo PATH: $PATH && which hdfs && {command}'"
    subprocess.run(full_command, shell=True, check=True)

# Function to read CSV and convert to Parquet
def csv_to_parquet(csv_file, parquet_file):
    df = pd.read_csv(csv_file, names=columns, dtype=dtypes, skiprows=1)
    df['prcp'] = df['prcp'].fillna(0)
    table = pa.Table.from_pandas(df)
    pq.write_table(table, parquet_file)

# Function to upload Parquet file to HDFS without copying to the Docker container
def upload_to_hdfs(local_path, hdfs_path):
    hdfs_command = f"hdfs dfs -put - {hdfs_path}"
    with open(local_path, 'rb') as local_file:
        full_command = f"docker exec -i {docker_container_name} bash -c '{hdfs_command}'"
        process = subprocess.Popen(full_command, shell=True, stdin=subprocess.PIPE)
        process.communicate(input=local_file.read())

# List of CSV files
csv_files = ['dataset/central_west.csv',
             'dataset/north.csv',
             'dataset/northeast.csv',
             'dataset/south.csv',
             'dataset/southeast.csv']

# Using a temporary directory
with tempfile.TemporaryDirectory() as temp_dir:
    print(f"Using temporary directory: {temp_dir}")

    # Main loop for processing and uploading files
    for csv_file in csv_files:
        print(f"Processing {csv_file}...")
        parquet_file = os.path.join(temp_dir, f"{os.path.basename(csv_file).split('.')[0]}.parquet")
        csv_to_parquet(csv_file, parquet_file)

        # HDFS directory for each data lake
        hdfs_dir = f"/datalake/{os.path.basename(csv_file).split('.')[0]}"
        run_in_docker(f"hdfs dfs -test -d {hdfs_dir} || hdfs dfs -mkdir -p {hdfs_dir}")

        # Upload Parquet file to HDFS
        hdfs_path = f"{hdfs_dir}/{os.path.basename(csv_file).split('.')[0]}.parquet"
        upload_to_hdfs(parquet_file, hdfs_path)

        print(f"Completed processing {csv_file}.")
        time.sleep(1)  # Optional pause between files

    print("Data upload to HDFS completed.")