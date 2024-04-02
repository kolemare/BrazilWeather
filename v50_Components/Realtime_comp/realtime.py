import json
import threading
import datetime
import requests
import time
from comm import Comm


class Realtime:
    def __init__(self, city_province, apikey, configuration):
        # Load the city and province mapping data
        with open(city_province, 'r') as file:
            city_province_data = json.load(file)["city_province_mapping"]
            self.city_province_mapping = {region: data for item in city_province_data for region, data in item.items()}

        # Load the API key
        with open(apikey, 'r') as file:
            self.api_key = json.load(file)["key"]

        with open(configuration, 'r') as file:
            config_data = json.load(file)
            self.request_sleep = int(config_data["request_sleep"])
            self.default_sleep = int(config_data["default_sleep"])
            self.request_url = config_data["request_url"]

        self.realtime_tasks = []
        self.weather_data_accumulated = []
        self.running_thread = None
        self.comm = None
        self.shutdown_event = threading.Event()

    @staticmethod
    def sleep(period):
        time.sleep(period)

    def add_task(self, task):
        self.comm.send_info(f"Adding {task} to configuration...")
        if task not in self.realtime_tasks:
            self.realtime_tasks.append(task)

    def start_gathering_data(self):
        if self.running_thread is None or not self.running_thread.is_alive():
            self.comm.send_info(f"Starting acquisition thread in detached mode...")
            self.shutdown_event.clear()
            self.running_thread = threading.Thread(target=self.weather_data_thread)
            self.running_thread.start()

    def stop_gathering_data(self):
        self.comm.send_info(f"Stopping acquisition thread...")
        self.shutdown_event.set()
        if self.running_thread:
            self.running_thread.join()

    def weather_data_thread(self):
        while not self.shutdown_event.is_set():
            for region in self.realtime_tasks:
                self.fetch_weather_data_for_region(region)
                if self.shutdown_event.is_set():
                    break

    @staticmethod
    def degrees_to_direction(degrees):
        if 45 <= degrees < 135:
            return 'E'
        elif 135 <= degrees < 225:
            return 'S'
        elif 225 <= degrees < 315:
            return 'W'
        else:
            return 'N'

    def fetch_weather_data_for_region(self, region):
        for city_info in self.city_province_mapping.get(region, []):
            city = city_info["city"]
            province = city_info["province"]
            response = self.send_weather_api_request(city)

            if response and response.status_code == 200:
                data = response.json()
                current_time = datetime.datetime.utcnow()  # Get the current UTC time
                temperature_celsius = round(data['main']['temp'] - 273.15, 2)  # Convert from Kelvin to Celsius
                temperature_fahrenheit = (temperature_celsius * 9 / 5) + 32  # Convert from Celsius to Fahrenheit
                humidity = data['main']['humidity']

                # Calculate THI
                thi = temperature_fahrenheit - ((0.55 - (0.55 * humidity / 100)) * (temperature_fahrenheit - 58))

                # Determine wind direction
                wind_direction = self.degrees_to_direction(data['wind']['deg'])

                weather_data = {
                    'temperature': temperature_celsius,
                    'pressure': data['main']['pressure'],
                    'humidity': humidity,
                    'wind_speed': data['wind']['speed'],
                    'wind_degrees': data['wind']['deg'],
                    'wind_direction': wind_direction,  # Add wind direction to the weather data
                    'prov': province,
                    'region': region,
                    'date': int(current_time.timestamp()),  # Convert to UNIX timestamp
                    'month': current_time.month,
                    'thi': round(thi, 2)  # Add THI to the weather data
                }
                self.weather_data_accumulated.append(weather_data)
                if len(self.weather_data_accumulated) >= 60:
                    self.comm.send_info("Handling accumulated data...")
                    self.handle_accumulated_data()
                    self.weather_data_accumulated.clear()

            if self.shutdown_event.is_set():
                break
            time.sleep(self.request_sleep)

    def send_weather_api_request(self, city):
        try:
            response = requests.get(f"{self.request_url}q={city}&appid={self.api_key}")
            return response
        except requests.RequestException as e:
            self.comm.send_info("Gathering information for weather failed.")
            return None

    def handle_accumulated_data(self):
        payload = f"realtime_data:{json.dumps(self.weather_data_accumulated)}"
        self.comm.send_info("Sending the results to DAO...")
        self.comm.client.publish("database", payload)
        self.sleep(self.default_sleep)
        self.weather_data_accumulated.clear()

    def handle_request(self, payload):
        parts = payload.split(":")
        if len(parts) != 3:
            self.comm.send_info("Invalid message format received.")
            return "command:invalid"
        request_id, command, parameter = parts
        if command == "configuration":
            self.comm.send_info(f"Received configuration to process {parameter}")
            self.add_task(parameter)
            return f"{request_id}:{command}:{parameter}:success"
        elif command == "start" and parameter == "realtime":
            self.comm.send_info("Starting realtime processing...")
            self.start_gathering_data()
            return f"{request_id}:start:success"
        elif command == "alive" and parameter == "request":
            self.comm.send_info("Alive => Running...")
            return f"{request_id}:realtime:alive:waiting"
        elif command == "shutdown":
            self.comm.send_info("Received shutdown command!")
            self.stop_gathering_data()
            self.shutdown_event.set()
            return f"{request_id}:realtime:{command}:acknowledged"
        else:
            self.comm.send_info(f"Unknown command: {command}")
            return f"{request_id}:{command}:{parameter}:error"


def main():
    realtime = Realtime('city_province.json', 'apikey.json', 'configuration.json')
    realtime.comm = Comm("mqtt-broker", "realtime", "response")
    realtime.comm.start(realtime.handle_request)
    realtime.shutdown_event.wait()
    realtime.comm.send_info("Shutting down communication...")
    realtime.comm.send_info("Shutting down...")
    realtime.comm.stop()


if __name__ == "__main__":
    main()
