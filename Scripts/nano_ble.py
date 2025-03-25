import os
import re
import serial
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation


class NanoBLE: 
    def __init__(self, port, baudrate=115200, timeout=1):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial = None
        self.connected = False

    def connect(self):
        try:
            self.serial = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
            self.connected = True
            print(f"Connected to {self.port} at {self.baudrate} baud.")
        except serial.SerialException as e:
            print(f"Error connecting to {self.port}: {e}")
            self.connected = False

    def disconnect(self):
        if self.serial and self.serial.is_open:
            self.serial.close()
            print(f"Disconnected from {self.port}.")
            self.connected = False
        else:
            print("Serial port is not open.")   
    
    def read_data(self):
        if self.connected:
            try:
                while True:
                    if self.serial.in_waiting > 0:
                        data = self.serial.readline().decode('utf-8').strip()
                        # print(f"{data}")
                        return data
            except KeyboardInterrupt:
                print("\nRead operation interrupted by user.")
                self.disconnect()
            except serial.SerialException as e:
                print(f"Error reading from {self.port}: {e}")
                self.disconnect()
        else:
            print("Serial por is not connected.")


    def save_data_to_txt(self, data, filename, path='C:/Users/JooRg/MicroPython/.venv/Data'):
        if not os.path.exists(path):
            os.makedirs(path)  

        filepath = os.path.join(path, filename) 

        file_exists = os.path.exists(filepath)

        with open(filepath, mode='a', encoding='utf-8') as file:
            if not file_exists:
                header = "A_X; A_Y; A_Z; G_X; G_Y; G_Z; B_X; B_Y; B_Z\n"
                file.write(header)

       
            file.write(data + '\n')  
        print(f"Data saved to {filepath}.")

    def format_data(self, raw_data):
        matches = re.findall(r"[-+]?\d*\.\d+|\d+", raw_data)
        return "; ".join(matches).replace('.',',')  
    
    def fixed_text(self, filename='test.txt', path='C:/Users/JooRg/MicroPython/.venv/Data'):
        if not os.path.exists(path):
            os.makedirs(path)
        filepath = os.path.join(path, filename)
        with open(filepath, mode='w', encoding='utf-8') as file:
            file.write("Test fixed text\n")




class DataVisio:
    def __init__(self, interval=5, max_points=100):
        self.max_points = max_points
        self.interval = interval
        self.data = [] 
        self.fig, self.ax = plt.subplots()  
        self.acc_mean_line, = self.ax.plot([], [], label="Accelerometer (Mean)")
        self.acc_std_line, = self.ax.plot([], [], label="Accelerometer (Std. Dev.)")
        self.gyro_mean_line, = self.ax.plot([], [], label="Gyroscope (Mean)")
        self.gyro_std_line, = self.ax.plot([], [], label="Gyroscope (Std. Dev.)")
        self.mag_mean_line, = self.ax.plot([], [], label="Magnetometer (Mean)")
        self.mag_std_line, = self.ax.plot([], [], label="Magnetometer (Std. Dev.)")

        self.ax.legend()
        self.acc_mean_history = []
        self.acc_std_history = []
        self.gyro_mean_history = []
        self.gyro_std_history = []
        self.mag_mean_history = []
        self.mag_std_history = []

    def update_data(self, new_data):
        self.data.append(new_data)
        if len(self.data) > self.interval:
            self.data.pop(0)  

    def calculate_modules(self):
        if len(self.data) == 0:
            return [],[],[]
        
        data_array = np.array(self.data)

        if data_array.shape[1] != 9:
            print("Error: Los datos no tienen el formato esperado (9 columnas).")
            return [], [], []
        acc_modules = np.sqrt(np.sum(data_array[:, 0:3]**2, axis=1))  
        gyro_modules = np.sqrt(np.sum(data_array[:, 3:6]**2, axis=1))  
        mag_modules = np.sqrt(np.sum(data_array[:, 6:9]**2, axis=1))  
        return acc_modules, gyro_modules, mag_modules        


    def calculate_statistics(self):
        acc_modules, gyro_modules, mag_modules = self.calculate_modules()
        stats = {
            "acc_mean": np.mean(acc_modules) if len(acc_modules) > 0 else 0,
            "acc_std": np.std(acc_modules) if len(acc_modules) > 0 else 0,
            "gyro_mean": np.mean(gyro_modules) if len(gyro_modules) > 0 else 0,
            "gyro_std": np.std(gyro_modules) if len(gyro_modules) > 0 else 0,
            "mag_mean": np.mean(mag_modules) if len(mag_modules) > 0 else 0,
            "mag_std": np.std(mag_modules) if len(mag_modules) > 0 else 0,
        }
        return stats

    def update_plot(self, frame):
        stats = self.calculate_statistics()
        self.acc_mean_history.append(stats["acc_mean"])
        self.acc_std_history.append(stats["acc_std"])
        self.gyro_mean_history.append(stats["gyro_mean"])
        self.gyro_std_history.append(stats["gyro_std"])
        self.mag_mean_history.append(stats["mag_mean"])
        self.mag_std_history.append(stats["mag_std"])
        if len(self.acc_mean_history) > self.max_points:
            self.acc_mean_history.pop(0)
            self.acc_std_history.pop(0)
            self.gyro_mean_history.pop(0)
            self.gyro_std_history.pop(0)
            self.mag_mean_history.pop(0)
            self.mag_std_history.pop(0)

        self.acc_mean_line.set_data(range(len(self.acc_mean_history)), self.acc_mean_history)
        self.acc_std_line.set_data(range(len(self.acc_std_history)), self.acc_std_history)
        self.gyro_mean_line.set_data(range(len(self.gyro_mean_history)), self.gyro_mean_history)
        self.gyro_std_line.set_data(range(len(self.gyro_std_history)), self.gyro_std_history)
        self.mag_mean_line.set_data(range(len(self.mag_mean_history)), self.mag_mean_history)
        self.mag_std_line.set_data(range(len(self.mag_std_history)), self.mag_std_history)
        self.ax.relim()
        self.ax.autoscale_view()
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def start_visualization(self):
        plt.ion()  
        self.fig.show()

    def stop_visualization(self):
        plt.ioff() 
        plt.close(self.fig)