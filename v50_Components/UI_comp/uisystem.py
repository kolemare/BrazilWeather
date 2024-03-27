import threading
import time
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import paho.mqtt.client as mqtt
from comm import Comm


class UISystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Data Visualization UI")
        self.comm = Comm("mqtt-broker", "ui", "marshaller")
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
        self.operation_label = tk.Label(self.root, text="operation:")
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

    def ui_callback_show(self, payload):
        parts = payload.split(":")
        if len(parts) == 1:
            self.show_message(payload)
        elif len(parts) == 5:
            source, region, operation, period, state = parts
            if "marshaller" == source:
                if "success" == state:
                    pass  # Plot from database
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
            self.comm.client.publish("marshaller", f"{self.region_var.get()}:{self.operation_var.get()}:{int(self.numeric_entry.get())}")
            self.show_message("Requesting data availability...")


if __name__ == "__main__":
    root = tk.Tk()
    app = UISystem(root)
    app.comm.start(app.ui_callback_show)
    app.shutdown_event.wait()
    app.comm.send_info("Shutting down...")
    app.comm.stop()
    root.destroy()
