import time
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import paho.mqtt.client as mqtt


class UISystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Data Visualization UI")

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

    def ui_callback(self):
        pass

    def plot_data(self):
        # Check if all fields are filled
        if not self.region_var.get() or not self.operation_var.get() or not self.numeric_entry.get():
            # Clear the plot and display a message
            self.plot.clear()
            self.plot.text(0.5, 0.5, 'Please fill all fields', ha='center', va='center')
            self.canvas.draw()
        else:
            self.plot.clear()
            self.plot.text(0.5, 0.5, 'Requesting data availability', ha='center', va='center')
            self.canvas.draw()


            self.plot.clear()
            self.plot.plot([1, 2, 3, 4], [1, 4, 9, 16])
            self.canvas.draw()


if __name__ == "__main__":
    root = tk.Tk()
    app = UISystem(root)
    root.mainloop()
