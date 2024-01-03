import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import pyarrow.fs
import time
import os

# Column abbreviations
columns = ['date', 'hour', 'prcp', 'stp', 'smax', 'smin', 'gbrd', 'temp', 'dewp', 'tmax', 'tmin', 'dmax', 'dmin',
           'hmax', 'hmin', 'hmdy', 'wdct', 'gust', 'wdsp', 'regi', 'prov', 'wsnm', 'inme', 'lat', 'lon', 'elvt']

# Function to read CSV and convert to Parquet
def csv_to_parquet(csv_file, parquet_file):
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
    df = pd.read_csv(csv_file, names=columns, dtype=dtypes, skiprows=1)
    df['prcp'] = df['prcp'].fillna(0)
    os.makedirs(os.path.dirname(parquet_file), exist_ok=True)
    table = pa.Table.from_pandas(df)
    pq.write_table(table, parquet_file)

# Function to upload Parquet file to HDFS
def upload_to_hdfs(hadoop_fs, local_path, hdfs_path):
    with open(local_path, 'rb') as local_file:
        with hadoop_fs.open_output_stream(hdfs_path) as hdfs_file:
            hdfs_file.write(local_file.read())

# HDFS Configuration
hdfs_host = 'localhost'  # As per your Hadoop configuration
hdfs_port = 9000  # Default port, change if different in your setup
hadoop_fs = pyarrow.fs.HadoopFileSystem(hdfs_host, hdfs_port)

# List of CSV files
csv_files = ['dataset/central_west.csv',
             'dataset/north.csv',
             'dataset/northeast.csv',
             'dataset/south.csv',
             'dataset/southeast.csv']

for csv_file in csv_files:
    print(f"Processing {csv_file}...")
    parquet_file = f"hadoop/temp/{os.path.basename(csv_file).split('.')[0]}.parquet"
    csv_to_parquet(csv_file, parquet_file)

    # Create HDFS directory for each data lake
    hdfs_dir = f"/datalake/{os.path.basename(csv_file).split('.')[0]}"
    try:
        info = hadoop_fs.get_file_info(hdfs_dir)
        if info.type == pa.fs.FileType.NotFound:
            raise FileNotFoundError
        print(f"Directory {hdfs_dir} exists in HDFS.")
    except FileNotFoundError:
        hadoop_fs.create_dir(hdfs_dir)
        print(f"Created directory {hdfs_dir} in HDFS.")

    # Upload Parquet file to HDFS
    hdfs_path = f"{hdfs_dir}/{os.path.basename(csv_file).split('.')[0]}.parquet"
    upload_to_hdfs(hadoop_fs, parquet_file, hdfs_path)

    print(f"Completed processing {csv_file}.")
    time.sleep(1)  # Optional pause between files

print("Data upload to HDFS completed.")