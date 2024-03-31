import time
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import paho.mqtt.client as mqtt
from comm import Comm
from daohandler import DaoHandler
import pandas as pd
import sqlite3
import threading
import os
from PIL import Image, ImageTk
import seaborn as sns


class UISystem:
    def __init__(self, root):
        mqtt_broker_ip = os.getenv('MQTT_BROKER_IP', 'mqtt-broker')
        self.root = root
        self.root.title("Data Visualization UI")
        self.comm = Comm(mqtt_broker_ip, "ui", "database", "marshaller")
        self.shutdown_event = threading.Event()

        # Create a matplotlib figure
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.plot = self.figure.add_subplot(111)

        # Create a matplotlib canvas attached to the figure and the root Tkinter widget
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.root)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # Container frame for widgets
        widget_frame = tk.Frame(self.root)
        widget_frame.pack(side=tk.TOP, fill=tk.X)

        # First row of widgets
        first_row_frame = tk.Frame(widget_frame)
        first_row_frame.pack(side=tk.TOP, fill=tk.X)

        # Dropdown for region selection
        self.region_label = tk.Label(first_row_frame, text="Region:")
        self.region_label.pack(side=tk.LEFT)
        self.region_var = tk.StringVar()
        self.region_dropdown = ttk.Combobox(first_row_frame, textvariable=self.region_var,
                                            values=["central_west", "north", "northeast", "south", "southeast", "all"])
        self.region_dropdown.pack(side=tk.LEFT)

        # Dropdown for operation selection
        self.operation_label = tk.Label(first_row_frame, text="Operation:")
        self.operation_label.pack(side=tk.LEFT)
        self.operation_var = tk.StringVar()
        self.operation_dropdown = ttk.Combobox(first_row_frame, textvariable=self.operation_var,
                                               values=["avg_temp", "total_rainfall", "pressure_extremes", "wind_speed",
                                                       "solar_radiation", "wind_direction_distribution",
                                                       "humidity_variability", "thermal_humidity_index",
                                                       "dew_point_range", "air_temp_variability"])
        self.operation_dropdown.pack(side=tk.LEFT)

        # Entry box for numerical input
        self.numeric_entry = tk.Entry(first_row_frame, width=5)
        self.numeric_entry.pack(side=tk.LEFT)

        # Button
        self.button = tk.Button(first_row_frame, text="Request ", command=self.plot_data)
        self.button.pack(side=tk.LEFT)

        # Second row of widgets
        second_row_frame = tk.Frame(widget_frame)
        second_row_frame.pack(side=tk.TOP, fill=tk.X)

        # Label for real-time region selection
        self.rt_region_label = tk.Label(second_row_frame, text="Region:")
        self.rt_region_label.pack(side=tk.LEFT)

        # Dropdown for real-time region selection (same as the first region dropdown)
        self.rt_region_var = tk.StringVar()
        self.rt_region_dropdown = ttk.Combobox(second_row_frame, textvariable=self.rt_region_var,
                                               values=["central_west", "north", "northeast", "south", "southeast",
                                                       "all"])
        self.rt_region_dropdown.pack(side=tk.LEFT)

        # Label for real-time data type selection
        self.rt_data_label = tk.Label(second_row_frame, text="Operation:")
        self.rt_data_label.pack(side=tk.LEFT)

        # Dropdown for real-time data type selection
        self.rt_operation_var = tk.StringVar()
        self.rt_data_dropdown = ttk.Combobox(second_row_frame, textvariable=self.rt_operation_var,
                                             values=["temp_rt", "pressure_rt", "humidity_rt", "wind_speed_rt",
                                                     "wind_direction_rt"])
        self.rt_data_dropdown.pack(side=tk.LEFT)

        # Entry box for real-time numerical input (same as the first numeric entry)
        self.rt_numeric_entry = tk.Entry(second_row_frame, width=5)
        self.rt_numeric_entry.pack(side=tk.LEFT)

        # Button for real-time data request
        self.rt_button = tk.Button(second_row_frame, text="Realtime", command=self.realtime_plot)
        self.rt_button.pack(side=tk.LEFT)

        # Frame for the shutdown button
        shutdown_frame = tk.Frame(widget_frame)
        shutdown_frame.pack(side=tk.RIGHT, fill=tk.Y)

        # Shutdown button
        shutdown_icon = Image.open("utils/shutdown.png")
        shutdown_icon = shutdown_icon.resize((20, 20), Image.Resampling.LANCZOS)
        shutdown_photo = ImageTk.PhotoImage(shutdown_icon)
        self.shutdown_button = tk.Button(shutdown_frame, image=shutdown_photo, command=self.shutdown)
        self.shutdown_button.image = shutdown_photo
        self.shutdown_button.pack(side=tk.TOP)

        self.comm.send_ui_info("Initialized.")

    def ui_callback(self, payload, topic):
        print(payload)
        if "database" == topic:
            self.comm.send_dao_info("Received data, sending to database...")
            DaoHandler.write_to_db(payload)
        elif "ui" == topic:
            parts = payload.split(":")
            if len(parts) == 1:
                self.show_message(payload)
            elif len(parts) == 5:
                source, region, operation, period, state = parts
                if "marshaller" == source:
                    if "success" == state:
                        self.comm.send_ui_info("Received data is ready for plotting.")
                        self.query_and_plot(operation, region, int(period))
                    else:
                        self.show_message(payload)
                else:
                    self.show_message(payload)

    def show_message(self, message):
        self.plot.clear()
        self.plot.text(0.5, 0.5, message, ha='center', va='center')
        self.canvas.draw()

    def plot_data(self):
        # Check if all fields are filled
        if not self.region_var.get() or not self.operation_var.get() or not self.numeric_entry.get():
            # Clear the plot and display a message
            self.show_message("Please fill all fields")
        else:
            self.comm.client.publish("marshaller",
                                     f"{self.region_var.get()}:{self.operation_var.get()}:{int(self.numeric_entry.get())}")
            self.show_message("Requesting data availability...")

    def realtime_plot(self):
        # Check if all fields are filled
        if not self.rt_operation_var.get() or not self.rt_region_var.get() or not self.rt_numeric_entry.get():
            # Clear the plot and display a message
            self.show_message("Please fill all fields for real-time data")
        else:
            pass

    def query_and_plot(self, operation, region, period):
        self.comm.send_ui_info(f"Plotting {operation} for {region} for {period}.")
        if "avg_temp" == operation:
            self.plot_avg_temp(operation, region, period)
        elif "total_rainfall" == operation:
            self.plot_total_rainfall(operation, region, period)
        elif "pressure_extremes" == operation:
            self.plot_pressure_extremes(operation, region, period)
        elif "wind_speed" == operation:
            self.plot_wind_speed(operation, region, period)
        elif "solar_radiation" == operation:
            self.plot_total_solar_radiation(operation, region, period)
        elif "wind_direction_distribution" == operation:
            self.plot_wind_direction_heatmap(operation, region, period)
        elif "humidity_variability" == operation:
            self.plot_humidity_variability(operation, region, period)
        elif "thermal_humidity_index" == operation:
            self.plot_thermal_humidity_index(operation, region, period)
        elif "dew_point_range" == operation:
            self.plot_dew_point_range(operation, region, period)
        elif "air_temp_variability" == operation:
            self.plot_air_temp_variability(operation, region, period)
        else:
            pass

    def plot_avg_temp(self, operation, region, period):
        df = DaoHandler.get_table(operation, region, period)
        if not df.empty:
            self.plot.clear()
            df['date'] = pd.to_datetime(df['date'], unit='ms')  # Convert timestamp to datetime
            df.sort_values(by='date', inplace=True)  # Sort by date
            for prov in df['prov'].unique():
                prov_data = df[df['prov'] == prov]
                self.plot.plot(prov_data['date'], prov_data['avg_temp'], label=prov)
            self.plot.set_xlabel('Date')
            self.plot.set_ylabel('Average Temperature')
            self.plot.set_title(f'Average Temperature for {region}')
            self.plot.legend()
            self.canvas.draw()
        else:
            self.show_message("No data available")

    def plot_total_rainfall(self, operation, region, period):
        df = DaoHandler.get_table(operation, region, period)
        if not df.empty:
            self.plot.clear()

            # Convert 'date' from UNIX timestamp (ms) to datetime
            df['date'] = pd.to_datetime(df['date'], unit='ms')
            df.dropna(subset=['date'], inplace=True)  # Drop rows where 'date' is NaT after coercion

            # Group data by province and month-year, then sum total rainfall
            df['month_year'] = df['date'].dt.to_period('M')
            monthly_rainfall = df.groupby(['prov', 'month_year'])['total_rainfall'].sum().unstack('prov').fillna(0)
            monthly_rainfall.index = monthly_rainfall.index.strftime('%Y-%m')  # Format index for plotting

            monthly_rainfall.plot(kind='bar', ax=self.plot)

            # Set labels and title for the bar chart
            self.plot.set_xlabel('Date')
            self.plot.set_ylabel('Total Rainfall (mm)')
            self.plot.set_title(f'Total Rainfall for {region} by Province')
            self.plot.legend()

            # Draw the bar chart
            self.canvas.draw()

            # Prepare data for pie chart
            total_rainfall_by_prov = df.groupby('prov')['total_rainfall'].sum()

            # Create a separate figure for pie chart
            fig, ax = plt.subplots(figsize=(8, 8))
            ax.pie(total_rainfall_by_prov, labels=total_rainfall_by_prov.index, autopct='%1.1f%%', startangle=140)
            ax.set_title(f'Rainfall Distribution for {region}')
            plt.show()  # Display the pie chart in a new window
        else:
            self.show_message("No data available")

    def plot_pressure_extremes(self, operation, region, period):
        df = DaoHandler.get_table(operation, region, period)
        if not df.empty:
            self.plot.clear()
            df['date'] = pd.to_datetime(df['date'], unit='ms')  # Convert timestamp to datetime
            df.sort_values(by='date', inplace=True)  # Sort by date
            for prov in df['prov'].unique():
                prov_data = df[df['prov'] == prov]
                self.plot.plot(prov_data['date'], prov_data['max_pressure'], label=f'{prov} Max', linestyle='--')
                self.plot.plot(prov_data['date'], prov_data['min_pressure'], label=f'{prov} Min', linestyle='-.')
            self.plot.set_xlabel('Date')
            self.plot.set_ylabel('Pressure (mb)')
            self.plot.set_title(f'Pressure Extremes for {region}')
            self.plot.legend()
            self.canvas.draw()
        else:
            self.show_message("No data available!")

    def plot_wind_speed(self, operation, region, period):
        df = DaoHandler.get_table(operation, region, period)
        if not df.empty:
            self.plot.clear()
            df['date'] = pd.to_datetime(df['date'], unit='ms')  # Convert timestamp to datetime
            df.sort_values(by='date', inplace=True)  # Sort by date
            for prov in df['prov'].unique():
                prov_data = df[df['prov'] == prov]
                self.plot.scatter(prov_data['date'], prov_data['avg_wind_speed'], label=prov, marker='x')
            self.plot.set_xlabel('Date')
            self.plot.set_ylabel('Average Wind Speed (m/s)')
            self.plot.set_title(f'Average Wind Speed for {region}')
            self.plot.legend()
            self.canvas.draw()
        else:
            self.show_message("No data available!")

    def plot_total_solar_radiation(self, operation, region, period):
        df = DaoHandler.get_table(operation, region, period)
        if not df.empty:
            self.plot.clear()
            df['date'] = pd.to_datetime(df['date'], unit='ms')  # Convert timestamp to datetime
            df.sort_values(by='date', inplace=True)  # Sort by date
            for prov in df['prov'].unique():
                prov_data = df[df['prov'] == prov]
                self.plot.fill_between(prov_data['date'], prov_data['total_solar_radiation'], label=prov, alpha=0.5)
            self.plot.set_xlabel('Date')
            self.plot.set_ylabel('Total Solar Radiation (KJ/m²)')
            self.plot.set_title(f'Total Solar Radiation for {region}')
            self.plot.legend()
            self.canvas.draw()
        else:
            self.show_message("No data available!")

    def plot_wind_direction_heatmap(self, operation, region, period):
        df = DaoHandler.get_table(operation, region, period)
        if not df.empty:
            # Convert timestamps to datetime objects and create 'month_year'
            df['date'] = pd.to_datetime(df['date'], unit='ms')
            df['month_year'] = df['date'].dt.to_period('M').dt.strftime('%Y-%m')

            # Reshape the DataFrame to have 'month_year', 'prov', and the wind directions
            wind_direction_data = df.pivot_table(index='prov', columns='month_year', values=['N', 'E', 'S', 'W'],
                                                 aggfunc='sum')

            # Plot a heatmap for each wind direction
            fig, axs = plt.subplots(2, 2, figsize=(15, 10))  # Adjust the size as needed

            for i, direction in enumerate(['N', 'E', 'S', 'W']):
                sns.heatmap(wind_direction_data[direction].fillna(0), ax=axs[i // 2, i % 2], annot=True, fmt="g")
                axs[i // 2, i % 2].set_title(f'{direction} Wind Frequency')

            self.show_message("Heatmap shown in other window")

            plt.tight_layout()
            plt.show()
        else:
            self.show_message("No data available")

    def plot_humidity_variability(self, operation, region, period):
        df = DaoHandler.get_table(operation, region, period)
        if not df.empty:
            self.plot.clear()
            df['date'] = pd.to_datetime(df['date'], unit='ms')  # Convert timestamp to datetime
            df.sort_values(by='date', inplace=True)  # Sort by date

            # Plot standard deviation of humidity for each province
            for prov in df['prov'].unique():
                prov_data = df[df['prov'] == prov]
                self.plot.plot(prov_data['date'], prov_data['humidity_std_dev'], label=prov, marker='o')

            self.plot.set_xlabel('Date')
            self.plot.set_ylabel('Humidity Standard Deviation (%)')
            self.plot.set_title(f'Humidity Variability for {region}')
            self.plot.legend()

            # Draw the plot
            self.canvas.draw()
        else:
            self.show_message("No data available")

    def plot_thermal_humidity_index(self, operation, region, period):
        df = DaoHandler.get_table(operation, region, period)
        if not df.empty:
            self.plot.clear()
            df['date'] = pd.to_datetime(df['date'], unit='ms')  # Convert timestamp to datetime
            df.sort_values(by='date', inplace=True)  # Sort by date

            # Plot average THI for each province
            for prov in df['prov'].unique():
                prov_data = df[df['prov'] == prov]
                self.plot.plot(prov_data['date'], prov_data['avg_thi'], label=prov, linestyle='-', marker='s')

            self.plot.set_xlabel('Date')
            self.plot.set_ylabel('Average THI')
            self.plot.set_title(f'Average Temperature-Humidity Index for {region}')
            self.plot.legend()

            # Draw the plot
            self.canvas.draw()
        else:
            self.show_message("No data available")

    def plot_dew_point_range(self, operation, region, period):
        df = DaoHandler.get_table(operation, region, period)
        if not df.empty:
            self.plot.clear()
            df['date'] = pd.to_datetime(df['date'], unit='ms')  # Convert timestamp to datetime
            df.sort_values(by='date', inplace=True)  # Sort by date

            # Plot dew point range for each province
            for prov in df['prov'].unique():
                prov_data = df[df['prov'] == prov]
                self.plot.bar(prov_data['date'], prov_data['dew_point_range'], label=prov, alpha=0.7)

            self.plot.set_xlabel('Date')
            self.plot.set_ylabel('Dew Point Range (°C)')
            self.plot.set_title(f'Dew Point Range for {region}')
            self.plot.legend()

            # Draw the plot
            self.canvas.draw()
        else:
            self.show_message("No data available")

    def plot_air_temp_variability(self, operation, region, period):
        df = DaoHandler.get_table(operation, region, period)
        if not df.empty:
            self.plot.clear()
            df['date'] = pd.to_datetime(df['date'], unit='ms')  # Convert timestamp to datetime
            df.sort_values(by='date', inplace=True)  # Sort by date

            # Plot air temperature variability for each province
            for prov in df['prov'].unique():
                prov_data = df[df['prov'] == prov]
                self.plot.errorbar(prov_data['date'], prov_data['temp_std_dev'], label=prov, fmt='-o', capsize=5)

            self.plot.set_xlabel('Date')
            self.plot.set_ylabel('Air Temperature Variability (°C)')
            self.plot.set_title(f'Air Temperature Variability for {region}')
            self.plot.legend()

            # Draw the plot
            self.canvas.draw()
        else:
            self.show_message("No data available")

    def shutdown(self):
        self.comm.send_ui_info("Requesting shutdown...")
        self.comm.client.publish("marshaller", f"{None}:shutdown:{None}")
        self.shutdown_event.set()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    ui = UISystem(root)
    ui.comm.start(ui.ui_callback)

    # Start the main event loop
    root.mainloop()

    # Shutdown logic
    ui.shutdown_event.wait()
    ui.comm.send_ui_info("Shutting down...")
    ui.comm.stop()
