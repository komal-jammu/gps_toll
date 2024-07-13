import random
from geopy.distance import geodesic
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from tkinter.simpledialog import askstring, askinteger, askfloat

# Define constants
TOLL_RADIUS = 5  # Radius in km to calculate toll
TOLL_MIN = 5  # Minimum toll amount
TOLL_MAX = 15  # Maximum toll amount
TRACK_INTERVAL = 1000  # Tracking interval in ms
NUM_POINTS = 10  # Number of points in vehicle path

# Define toll booth locations
toll_booths = {
    'Booth1': (28.7041, 77.1025),
    'Booth2': (19.0760, 72.8777),
    'Booth3': (13.0827, 80.2707)
}

def generate_vehicle_path(start, end, num_points=NUM_POINTS):
    lat_diff = (end[0] - start[0]) / num_points
    lon_diff = (end[1] - start[1]) / num_points
    path = [(start[0] + i * lat_diff, start[1] + i * lon_diff) for i in range(num_points + 1)]
    return path

class MockPaymentGateway:
    """Simulates a contactless payment gateway."""

    @staticmethod
    def process_payment(vehicle_id, booth_name, toll):
        """Simulate the payment process."""
        # Simulate a 20% chance of payment failure
        if random.random() < 0.2:
            messagebox.showerror("Payment Failed", f"Payment failed for Vehicle {vehicle_id} at {booth_name} booth.")
            return False
        # Simulate a 10% chance of payment delay
        elif random.random() < 0.1:
            messagebox.showinfo("Payment Delayed", f"Payment for Vehicle {vehicle_id} at {booth_name} booth is being processed. Please wait.")
            return None
        else:
            messagebox.showinfo("Payment Success", f"Payment of ${toll} succeeded for Vehicle {vehicle_id} at {booth_name} booth.")
            return True

def calculate_toll(vehicle_id, vehicle_position, toll_booths):
    tolls = {}
    total_toll = 0
    for booth_name, booth_location in toll_booths.items():
        distance = geodesic(vehicle_position, booth_location).kilometers
        if distance < TOLL_RADIUS:
            
            toll = random.randint(TOLL_MIN, TOLL_MAX)
            payment_result = MockPaymentGateway.process_payment(vehicle_id, booth_name, toll)
            if payment_result is False:
                return tolls, total_toll, False  # Payment denied
            elif payment_result is None:
                return tolls, total_toll, None  # Payment delayed
            else:
                tolls[booth_name] = toll
                total_toll += toll
    return tolls, total_toll, True  # Payment confirmed

def track_vehicles(self):
    """Track the vehicles and update their positions."""
    for i in range(self.num_vehicles):
        if self.tracking and self.vehicle_positions[i] < len(self.vehicle_paths[i]):
            current_position = self.vehicle_paths[i][self.vehicle_positions[i]]
            tolls, toll, payment_confirmed = calculate_toll(i+1, current_position, toll_booths)

            if payment_confirmed is False:
                self.stop_tracking()
                messagebox.showwarning("Tracking Stopped", f"Payment denied for Vehicle {i+1}. Stopping tracking.")
                return
            elif payment_confirmed is None:
                self.log_text.insert(tk.END, f"Vehicle {i+1} at {current_position} | Payment delayed.\n")
                self.vehicle_labels[i].config(text=f"Vehicle {i+1} Position: {current_position} | Payment delayed")
                continue

            self.total_tolls[i] += toll

            self.vehicle_labels[i].config(text=f"Vehicle {i+1} Position: {current_position}")
            self.toll_labels[i].config(text=f"Vehicle {i+1} Total Toll: ${self.total_tolls[i]}")
            self.log_text.insert(tk.END, f"Vehicle {i+1} at {current_position} | Tolls: {tolls} | Total Toll: ${self.total_tolls[i]}\n")

            self.vehicle_positions[i] += 1

            if self.vehicle_positions[i] == len(self.vehicle_paths[i]):
                self.log_text.insert(tk.END, f"Vehicle {i+1} has reached the destination.\n")

    self.update_graph()
    if self.tracking:
        self.root.after(TRACK_INTERVAL, self.track_vehicles)


def calculate_toll(vehicle_id, vehicle_position, toll_booths):
    tolls = {}
    total_toll = 0
    for booth_name, booth_location in toll_booths.items():
        distance = geodesic(vehicle_position, booth_location).kilometers
        if distance < TOLL_RADIUS:
            toll = random.randint(TOLL_MIN, TOLL_MAX)
            if MockPaymentGateway.process_payment(vehicle_id, booth_name, toll):
                tolls[booth_name] = toll
                total_toll += toll
            else:
                return tolls, total_toll, False  # Payment denied
    return tolls, total_toll, True  # Payment confirmed

class TollSystemApp:
    def __init__(self, root, num_vehicles=3):
        self.root = root
        self.root.title("GPS Toll System Simulation")

        self.setup_ui()
        self.num_vehicles = num_vehicles

        self.vehicle_labels = []
        self.toll_labels = []
        self.vehicle_positions = []
        self.vehicle_paths = []
        self.total_tolls = []
        self.vehicle_colors = []
        self.tracking = False

        self.initialize_vehicles()

    def setup_ui(self):
        """Set up the user interface."""
        self.label = tk.Label(self.root, text="Toll System Simulation", font=("Helvetica", 16))
        self.label.pack(pady=10)

        self.frame = tk.Frame(self.root)
        self.frame.pack(pady=10)

        self.start_button = tk.Button(self.frame, text="Start Tracking", command=self.start_tracking, font=("Helvetica", 12))
        self.start_button.grid(row=0, column=0, padx=10)

        self.stop_button = tk.Button(self.frame, text="Stop Tracking", command=self.stop_tracking, state=tk.DISABLED, font=("Helvetica", 12))
        self.stop_button.grid(row=0, column=1, padx=10)

        self.add_booth_button = tk.Button(self.frame, text="Add Toll Booth", command=self.add_toll_booth, font=("Helvetica", 12))
        self.add_booth_button.grid(row=0, column=2, padx=10)

        self.reset_button = tk.Button(self.frame, text="Reset", command=self.reset_simulation, font=("Helvetica", 12))
        self.reset_button.grid(row=0, column=3, padx=10)

        self.canvas_frame = tk.Frame(self.root)
        self.canvas_frame.pack()

        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.canvas_frame)
        self.canvas.get_tk_widget().pack()

        self.log_text = tk.Text(self.root, height=10, width=50, font=("Helvetica", 12))
        self.log_text.pack(pady=10)

    def initialize_vehicles(self):
        """Initialize vehicledata."""
        for i in range(self.num_vehicles):
            vehicle_label = tk.Label(self.root, text=f"Vehicle {i+1} Position: N/A", font=("Helvetica", 12))
            vehicle_label.pack()
            self.vehicle_labels.append(vehicle_label)

            toll_label = tk.Label(self.root, text=f"Vehicle {i+1} Total Toll: $0", font=("Helvetica", 12))
            toll_label.pack()
            self.toll_labels.append(toll_label)

            start = random.choice(list(toll_booths.values()))
            end = random.choice(list(toll_booths.values()))
            path = generate_vehicle_path(start, end)
            self.vehicle_paths.append(path)
            self.vehicle_positions.append(0)
            self.total_tolls.append(0)
            self.vehicle_colors.append((random.random(), random.random(), random.random()))

    def start_tracking(self):
        """Start tracking vehicles."""
        self.tracking = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.track_vehicles()

    def stop_tracking(self):
        """Stop tracking vehicles."""
        self.tracking = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def add_toll_booth(self):
        """Add a new toll booth."""
        try:
            booth_name = askstring("Add Toll Booth", "Enter toll booth name:")
            if not booth_name:
                return
            booth_lat = askfloat("Add Toll Booth", "Enter latitude:")
            booth_lon = askfloat("Add Toll Booth", "Enter longitude:")
            toll_booths[booth_name] = (booth_lat, booth_lon)
            self.log_text.insert(tk.END, f"Toll booth '{booth_name}' added at ({booth_lat}, {booth_lon}).\n")
            messagebox.showinfo("Success", f"Toll booth '{booth_name}' added at ({booth_lat}, {booth_lon}).")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add toll booth: {e}")

    def update_graph(self):
        """Update the graph with vehicle positions and paths."""
        self.ax.clear()
        self.ax.set_title('Vehicle Positions and Paths')
        self.ax.set_xlabel('Longitude')
        self.ax.set_ylabel('Latitude')

        for booth_name, booth_location in toll_booths.items():
            self.ax.plot(booth_location[1], booth_location[0], 'ro')
            self.ax.text(booth_location[1], booth_location[0], booth_name, fontsize=12, ha='right')

        for i in range(self.num_vehicles):
            path = np.array(self.vehicle_paths[i])
            current_position = self.vehicle_positions[i]

            self.ax.plot(path[:, 1], path[:, 0], linestyle='--', color=self.vehicle_colors[i])
            if current_position < len(path):
                self.ax.plot(path[current_position, 1], path[current_position, 0], 'go', color=self.vehicle_colors[i])
                self.ax.text(path[current_position, 1], path[current_position, 0], f'V{i+1}\n${self.total_tolls[i]}', fontsize=12, ha='left')

        self.ax.legend([f'Vehicle {i+1}' for i in range(self.num_vehicles)])
        self.canvas.draw()

    def track_vehicles(self):
        """Track the vehicles and update their positions."""
        for i in range(self.num_vehicles):
            if self.tracking and self.vehicle_positions[i] < len(self.vehicle_paths[i]):
                current_position = self.vehicle_paths[i][self.vehicle_positions[i]]
                tolls, toll, payment_confirmed = calculate_toll(i+1, current_position, toll_booths)

                if not payment_confirmed:
                    self.stop_tracking()
                    messagebox.showwarning("Tracking Stopped", f"Payment denied for Vehicle {i+1}. Stopping tracking.")
                    return

                self.total_tolls[i] += toll

                self.vehicle_labels[i].config(text=f"Vehicle {i+1} Position: {current_position}")
                self.toll_labels[i].config(text=f"Vehicle {i+1} Total Toll: ${self.total_tolls[i]}")
                self.log_text.insert(tk.END, f"Vehicle {i+1} at {current_position} | Tolls: {tolls} | Total Toll: ${self.total_tolls[i]}\n")

                self.vehicle_positions[i] += 1

                if self.vehicle_positions[i] == len(self.vehicle_paths[i]):
                    self.log_text.insert(tk.END, f"Vehicle {i+1} has reached the destination.\n")

        self.update_graph()
        if self.tracking:
            self.root.after(TRACK_INTERVAL, self.track_vehicles)

    def reset_simulation(self):
        """Reset the simulation to initial state."""
        self.tracking= False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

        self.vehicle_positions = [0] * self.num_vehicles
        self.total_tolls = [0] * self.num_vehicles
        self.vehicle_paths = []

        for i in range(self.num_vehicles):
            start = random.choice(list(toll_booths.values()))
            end = random.choice(list(toll_booths.values()))
            self.vehicle_paths.append(generate_vehicle_path(start, end))

        self.update_graph()
        self.log_text.delete(1.0, tk.END)
        for i in range(self.num_vehicles):
            self.vehicle_labels[i].config(text=f"Vehicle {i+1} Position: N/A")
            self.toll_labels[i].config(text=f"Vehicle {i+1} Total Toll: $0")

if __name__ == "__main__":
    root = tk.Tk()

    num_vehicles = askinteger("Number of Vehicles", "Enter the number of vehicles to track:")
    if num_vehicles is None:
        num_vehicles = 3

    app = TollSystemApp(root, num_vehicles=num_vehicles)
    root.mainloop()