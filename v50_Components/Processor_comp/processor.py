import os
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import threading
from comm import Comm
from calculator import Calculator
from hdfs import InsecureClient


class Processor:
    def __init__(self, hdfs_host, hdfs_port, hdfs_user):
        self.hdfs_client = InsecureClient(f"{hdfs_host}:{hdfs_port}", user=hdfs_user)
        self.shutdown_event = threading.Event()
        self.comm = Comm("mqtt-broker", "processor", "response")
        self.region = None
        self.data = None

    def check_read_parquet_from_hdfs(self, region):
        if region == self.region:
            return True
        self.comm.send_info(f"Reading data for: {region}")
        hdfs_path = f"/datalake/curated/{region}.parquet"
        try:
            with self.hdfs_client.read(hdfs_path) as reader:
                data = reader.read()
                self.data = pq.read_table(pa.BufferReader(data)).to_pandas()
                self.comm.send_info(f"Data for {region} loaded successfully.")
                self.region = region
                return True
        except Exception as e:
            self.comm.send_info(f"Failed to load data for {region}: {e}")
            self.data[region] = None
            return False

    def handle_request(self, payload):
        parts = payload.split(":")
        if len(parts) == 3:
            request_id, command, item = parts
            if command == "shutdown":
                self.comm.send_info("Received shutdown command!")
                self.shutdown_event.set()
                return f"{request_id}:processor:{command}:acknowledged"
            elif command == "alive" and item == "request":
                self.comm.send_info("Alive => Running...")
                return f"{request_id}:processor:alive:waiting"
            else:
                self.comm.send_info(f"Unknown command: {command}")
                return f"{request_id}:{command}:{item}:error"
        if len(parts) == 4:
            request_id, calculation, region, period = parts
            if calculation == "avg_temp" and self.check_read_parquet_from_hdfs(region):
                result = Calculator.calculate_avg_temp(region, self.data, int(period))
            elif calculation == "total_rainfall" and self.check_read_parquet_from_hdfs(region):
                result = Calculator.calculate_total_rainfall(region, self.data, int(period))
            elif calculation == "pressure_extremes" and self.check_read_parquet_from_hdfs(region):
                result = Calculator.calculate_pressure_extremes(region, self.data, int(period))
            elif calculation == "wind_speed" and self.check_read_parquet_from_hdfs(region):
                result = Calculator.calculate_wind_speed(region, self.data, int(period))
            elif calculation == "solar_radiation" and self.check_read_parquet_from_hdfs(region):
                result = Calculator.calculate_total_solar_radiation(region, self.data, int(period))
            elif calculation == "wind_direction_distribution" and self.check_read_parquet_from_hdfs(region):
                result = Calculator.calculate_wind_direction_distribution(region, self.data, int(period))
            elif calculation == "humidity_variability" and self.check_read_parquet_from_hdfs(region):
                result = Calculator.calculate_humidity_variability(region, self.data, int(period))
            elif calculation == "thermal_humidity_index" and self.check_read_parquet_from_hdfs(region):
                result = Calculator.calculate_thi(region, self.data, int(period))
            elif calculation == "dew_point_range" and self.check_read_parquet_from_hdfs(region):
                result = Calculator.calculate_dew_point_range(region, self.data, int(period))
            elif calculation == "air_temp_variability" and self.check_read_parquet_from_hdfs(region):
                result = Calculator.calculate_air_temp_variability(region, self.data, int(period))
            else:
                return f"{request_id}:{calculation}:{region}:{period}:failure"
            result_str = result.to_json()
            self.comm.send_info(f"Successfully finished processing:{calculation} for {region} duration: {period}")
            self.comm.send_info(f"Sending result to DAO: {calculation} for {region} for {period}")
            self.comm.client.publish("database", f"{calculation}:{result_str}")
            return f"{request_id}:{calculation}:{region}:{period}:success"


def main():
    processor = Processor('http://hadoop-container', 9870, 'root')
    processor.comm.start(processor.handle_request)
    processor.shutdown_event.wait()
    processor.comm.send_info("Shutting down communication...")
    processor.comm.send_info("Shutting down...")
    processor.comm.stop()


if __name__ == "__main__":
    main()
