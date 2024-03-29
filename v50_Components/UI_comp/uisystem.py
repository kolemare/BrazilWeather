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

        # Dropdown for region selection
        self.region_label = tk.Label(self.root, text="Region:")
        self.region_label.pack(side=tk.LEFT)
        self.region_var = tk.StringVar()
        self.region_dropdown = ttk.Combobox(self.root, textvariable=self.region_var,
                                            values=["central_west", "north", "northeast", "south", "southeast", "all"])
        self.region_dropdown.pack(side=tk.LEFT)

        # Dropdown for operation selection
        self.operation_label = tk.Label(self.root, text="Operation:")
        self.operation_label.pack(side=tk.LEFT)
        self.operation_var = tk.StringVar()
        self.operation_dropdown = ttk.Combobox(self.root, textvariable=self.operation_var,
                                               values=["avg_temp", "total_rainfall", "pressure_extremes"])
        self.operation_dropdown.pack(side=tk.LEFT)

        # Entry box for numerical input
        self.numeric_entry = tk.Entry(self.root, width=5)
        self.numeric_entry.pack(side=tk.LEFT)

        # Button
        self.button = tk.Button(self.root, text="Plot", command=self.plot_data)
        self.button.pack(side=tk.LEFT)

    def ui_callback(self, payload, topic):
        self.show_message(payload)
        if "database" == topic:
            DaoHandler.write_to_db(payload)
        elif "ui" == topic:
            parts = payload.split(":")
            if len(parts) == 1:
                self.show_message(payload)
            elif len(parts) == 5:
                source, region, operation, period, state = parts
                if "marshaller" == source:
                    if "success" == state:
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

    def query_and_plot(self, operation, region, period):
        if "avg_temp" == operation:
            self.plot_avg_temp(operation, region, period)
        elif "total_rainfall" == operation:
            self.plot_total_rainfall(operation, region, period * 12)
        elif "pressure_extremes" == operation:
            self.plot_pressure_extremes(operation, region, period)
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
        print(df)

    def plot_pressure_extremes(self, operation, region, period):
        df = DaoHandler.get_table(operation, region, period)
        print(df)



if __name__ == "__main__":
    root = tk.Tk()
    ui = UISystem(root)
    ui.comm.start(ui.ui_callback)

    # Start the main event loop
    root.mainloop()

    # Shutdown logic
    ui.shutdown_event.wait()
    ui.comm.send_info("Shutting down...")
    ui.comm.stop()
    root.destroy()
