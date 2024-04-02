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
import numpy as np
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

        # Button for real-time data request
        self.rt_button = tk.Button(first_row_frame, text="Realtime", command=self.realtime_plot)
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
            self.show_message("Requesting history data availability...")

    def realtime_plot(self):
        # Check if all fields are filled
        if not self.operation_var.get() or not self.region_var.get() or not self.numeric_entry.get():
            # Clear the plot and display a message
            self.show_message("Please fill all fields for real-time data")
        else:
            if self.region_var.get() == "all":
                self.show_message(f"System does not support realtime processing for all regions.")
            elif self.operation_var.get() == "avg_temp":
                self.plot_realtime_temp(self.operation_var.get(), self.region_var.get(), int(self.numeric_entry.get()))
            elif self.operation_var.get() == "pressure_extremes":
                self.plot_realtime_pressure(self.operation_var.get(), self.region_var.get(), int(self.numeric_entry.get()))
            elif self.operation_var.get() == "thermal_humidity_index":
                self.plot_realtime_thi(self.operation_var.get(), self.region_var.get(), int(self.numeric_entry.get()))
            elif self.operation_var.get() == "wind_speed":
                self.plot_realtime_wind_speed(self.operation_var.get(), self.region_var.get(), int(self.numeric_entry.get()))
            elif self.operation_var.get() == "wind_direction_distribution":
                self.plot_realtime_wind_direction_probability(self.operation_var.get(), self.region_var.get(), int(self.numeric_entry.get()))
            else:
                self.show_message(f"System does not support realtime processing for {self.operation_var.get()}")

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

    def plot_realtime_temp(self, operation, region, period):
        self.show_message("No data available for plotting.")
        # First, fetch the historical and real-time data
        df_history = DaoHandler.get_table(operation, region, period)
        realtime_df = DaoHandler.get_realtime_table(region)

        # Check if the DataFrames are not empty
        if not df_history.empty and not realtime_df.empty:
            # Calculate average temperature per province in the real-time DataFrame
            realtime_avg_temp = (
                realtime_df
                .groupby('prov')['temperature']
                .mean()
                .reset_index()
                .rename(columns={'temperature': 'avg_realtime_temp'})
            )
            # Combine historical and real-time data
            combined_data = pd.merge(
                df_history[['prov', 'avg_temp', 'year', 'month']],
                realtime_avg_temp,
                on='prov',
                how='inner'
            )
            # If there's no matching data after filtering, show a message and exit
            if combined_data.empty:
                self.show_message(f"No data available for {period}")
                return

            # Set up bar positions
            n = len(combined_data)
            index = np.arange(n)
            bar_width = 0.35

            # Convert the 'date' column to datetime format
            df_history['date'] = pd.to_datetime(df_history['date'], unit='ms')

            # Calculate the minimum and maximum dates
            min_date = df_history['date'].min().strftime('%Y-%m-%d')
            max_date = df_history['date'].max().strftime('%Y-%m-%d')

            self.plot.clear()

            # Create bars for average and real-time temperatures
            self.plot.bar(index, combined_data['avg_temp'], bar_width, label='Average Temp', color='blue')
            self.plot.bar(index + bar_width, combined_data['avg_realtime_temp'], bar_width, label='Real-time Temp',
                          color='red', alpha=0.5)

            # Set plot labels and title
            self.plot.set_xlabel('Province')
            self.plot.set_ylabel('Temperature (°C)')
            self.plot.set_title(f'Real-time vs Average Temperature for {region} from {min_date} to {max_date}')
            self.plot.set_xticks(index + bar_width / 2)
            self.plot.set_xticklabels(combined_data['prov'], rotation=45)

            # Show legend
            self.plot.legend()

            # Draw the updated plot
            self.canvas.draw()
        else:
            self.show_message("No data available for plotting.")

    def plot_realtime_pressure(self, operation, region, period):
        self.show_message("No data available for plotting.")
        # First, fetch the historical and real-time data
        df_history = DaoHandler.get_table(operation, region, period)
        realtime_df = DaoHandler.get_realtime_table(region)

        # Check if the DataFrames are not empty
        if not df_history.empty and not realtime_df.empty:
            # Calculate average pressure per province in the real-time DataFrame
            realtime_avg_pressure = (
                realtime_df
                .groupby('prov')['pressure']
                .mean()
                .reset_index()
                .rename(columns={'pressure': 'avg_realtime_pressure'})
            )

            # Combine historical and real-time data
            combined_data = pd.merge(
                df_history[['prov', 'min_pressure', 'max_pressure', 'date']],
                realtime_avg_pressure,
                on='prov',
                how='inner'
            )

            # Convert the 'date' column to datetime format
            combined_data['date'] = pd.to_datetime(combined_data['date'], unit='ms')

            # Calculate the minimum and maximum dates
            min_date = combined_data['date'].min().strftime('%Y-%m-%d')
            max_date = combined_data['date'].max().strftime('%Y-%m-%d')

            # Calculate pressure differences
            combined_data['pressure_above_min'] = (
                    (combined_data['avg_realtime_pressure'] - combined_data['min_pressure']) / combined_data['min_pressure'] * 100
            )
            combined_data['pressure_below_max'] = (
                    (combined_data['max_pressure'] - combined_data['avg_realtime_pressure']) / combined_data['max_pressure'] * 100
            )

            # If there's no matching data after filtering, show a message and exit
            if combined_data.empty:
                self.show_message(f"No data available for {period}")
                return

            # Set up bar positions
            n = len(combined_data)
            index = np.arange(n)
            bar_width = 0.35

            self.plot.clear()

            # Create bars for pressure differences
            self.plot.bar(index, combined_data['pressure_above_min'], bar_width, label='Pressure Above Min (%)',
                          color='blue')
            self.plot.bar(index + bar_width, combined_data['pressure_below_max'], bar_width,
                          label='Pressure Below Max (%)',
                          color='red', alpha=0.5)

            # Set plot labels and title
            self.plot.set_xlabel('Province')
            self.plot.set_ylabel('Pressure Difference (%)')
            self.plot.set_title(f'Pressure Differences for {region} from {min_date} to {max_date}')
            self.plot.set_xticks(index + bar_width / 2)
            self.plot.set_xticklabels(combined_data['prov'], rotation=45)

            # Show legend
            self.plot.legend()

            # Draw the updated plot
            self.canvas.draw()
        else:
            self.show_message("No data available for plotting.")

    def plot_realtime_thi(self, operation, region, period):
        self.show_message("No data available for plotting.")
        # First, fetch the historical and real-time data
        df_history = DaoHandler.get_table(operation, region, period)
        realtime_df = DaoHandler.get_realtime_table(region)

        # Check if the DataFrames are not empty
        if not df_history.empty and not realtime_df.empty:
            # Calculate average THI per province in the real-time DataFrame
            realtime_avg_thi = (
                realtime_df
                .groupby('prov')['thi']
                .mean()
                .reset_index()
                .rename(columns={'thi': 'avg_realtime_thi'})
            )

            # Combine historical and real-time data
            combined_data = pd.merge(
                df_history[['prov', 'avg_thi', 'year', 'month']],
                realtime_avg_thi,
                on='prov',
                how='inner'
            )

            # If there's no matching data after filtering, show a message and exit
            if combined_data.empty:
                self.show_message(f"No data available for {period}")
                return

            # Set up bar positions
            n = len(combined_data)
            index = np.arange(n)
            bar_width = 0.35

            # Convert the 'date' column to datetime format
            df_history['date'] = pd.to_datetime(df_history['date'], unit='ms')

            # Calculate the minimum and maximum dates
            min_date = df_history['date'].min().strftime('%Y-%m-%d')
            max_date = df_history['date'].max().strftime('%Y-%m-%d')

            self.plot.clear()

            # Create bars for average and real-time THI
            self.plot.bar(index, combined_data['avg_thi'], bar_width, label='Average THI', color='blue')
            self.plot.bar(index + bar_width, combined_data['avg_realtime_thi'], bar_width, label='Real-time THI',
                          color='red', alpha=0.5)

            # Set plot labels and title
            self.plot.set_xlabel('Province')
            self.plot.set_ylabel('THI')
            self.plot.set_title(f'Real-time vs Average THI for {region} from {min_date} to {max_date}')
            self.plot.set_xticks(index + bar_width / 2)
            self.plot.set_xticklabels(combined_data['prov'], rotation=45)

            # Show legend
            self.plot.legend()

            # Draw the updated plot
            self.canvas.draw()
        else:
            self.show_message("No data available for plotting.")

    def plot_realtime_wind_speed(self, operation, region, period):
        self.show_message("No data available for plotting.")
        # First, fetch the historical and real-time data
        df_history = DaoHandler.get_table(operation, region, period)
        realtime_df = DaoHandler.get_realtime_table(region)

        # Check if the DataFrames are not empty
        if not df_history.empty and not realtime_df.empty:
            # Calculate average wind speed per province in the real-time DataFrame
            realtime_avg_wind_speed = (
                realtime_df
                .groupby('prov')['wind_speed']
                .mean()
                .reset_index()
                .rename(columns={'wind_speed': 'avg_realtime_wind_speed'})
            )

            # Combine historical and real-time data
            combined_data = pd.merge(
                df_history[['prov', 'avg_wind_speed', 'year', 'month']],
                realtime_avg_wind_speed,
                on='prov',
                how='inner'
            )

            # If there's no matching data after filtering, show a message and exit
            if combined_data.empty:
                self.show_message(f"No data available for {period}")
                return

            # Set up bar positions
            n = len(combined_data)
            index = np.arange(n)
            bar_width = 0.35

            # Convert the 'date' column to datetime format
            df_history['date'] = pd.to_datetime(df_history['date'], unit='ms')

            # Calculate the minimum and maximum dates
            min_date = df_history['date'].min().strftime('%Y-%m-%d')
            max_date = df_history['date'].max().strftime('%Y-%m-%d')

            self.plot.clear()

            # Create bars for average and real-time wind speeds
            self.plot.bar(index, combined_data['avg_wind_speed'], bar_width, label='Average Wind Speed', color='blue')
            self.plot.bar(index + bar_width, combined_data['avg_realtime_wind_speed'], bar_width,
                          label='Real-time Wind Speed', color='red', alpha=0.5)

            # Set plot labels and title
            self.plot.set_xlabel('Province')
            self.plot.set_ylabel('Wind Speed (m/s)')
            self.plot.set_title(f'Real-time vs Average Wind Speed for {region} from {min_date} to {max_date}')
            self.plot.set_xticks(index + bar_width / 2)
            self.plot.set_xticklabels(combined_data['prov'], rotation=45)

            # Show legend
            self.plot.legend()

            # Draw the updated plot
            self.canvas.draw()
        else:
            self.show_message("No data available for plotting.")

    def plot_realtime_wind_direction_probability(self, operation, region, period):
        self.show_message("No data available for plotting.")
        # First, fetch the historical and real-time data
        df_history = DaoHandler.get_table(operation, region, period)
        realtime_df = DaoHandler.get_realtime_table(region)

        # Check if the DataFrames are not empty
        if not df_history.empty and not realtime_df.empty:
            # Calculate the average wind direction per province in the real-time DataFrame
            realtime_avg_wind_direction = (
                realtime_df
                .groupby('prov')['wind_direction']
                .apply(lambda x: x.mode().iloc[0] if not x.mode().empty else 'Unknown')
                .reset_index()
                .rename(columns={'wind_direction': 'avg_realtime_wind_direction'})
            )

            # Combine historical and real-time data
            combined_data = pd.merge(
                df_history[['prov', 'N', 'E', 'S', 'W', 'year', 'month']],
                realtime_avg_wind_direction,
                on='prov',
                how='inner'
            )

            # Calculate the total occurrences of each wind direction in the historical data
            combined_data['total_counts'] = combined_data[['N', 'E', 'S', 'W']].sum(axis=1)

            # Calculate the probability of the average wind direction
            combined_data['probability'] = combined_data.apply(
                lambda row: (row[row['avg_realtime_wind_direction']] / row['total_counts']) * 100 if row['total_counts'] > 0 else 0,
                axis=1
            )

            # Set up bar positions
            n = len(combined_data)
            index = np.arange(n)
            bar_width = 0.35

            # Convert the 'date' column to datetime format
            df_history['date'] = pd.to_datetime(df_history['date'], unit='ms')

            # Calculate the minimum and maximum dates
            min_date = df_history['date'].min().strftime('%Y-%m-%d')
            max_date = df_history['date'].max().strftime('%Y-%m-%d')

            self.plot.clear()

            # Create bars for wind direction probability
            self.plot.bar(index, combined_data['probability'], bar_width,
                          label=f'Probability of {combined_data["avg_realtime_wind_direction"].iloc[0]}', color='blue')

            # Set plot labels and title
            self.plot.set_xlabel('Province')
            self.plot.set_ylabel('Probability (%)')
            self.plot.set_title(
                f'Probability of Average Wind Direction for {region} from {min_date} to {max_date}')
            self.plot.set_xticks(index + bar_width / 2)
            self.plot.set_xticklabels(combined_data['prov'], rotation=45)

            # Show legend
            self.plot.legend()

            # Draw the updated plot
            self.canvas.draw()
        else:
            self.show_message("No data available for plotting.")

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
