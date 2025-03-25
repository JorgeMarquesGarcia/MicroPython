import sys
sys.path.append('C:/Users/JooRg/MicroPython/.venv/Scripts')
from nano_ble import NanoBLE
from nano_ble import DataVisio
import os
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

def get_filename(path='C:/Users/JooRg/MicroPython/.venv/Data'):
    while True:
        filename = input("Enter the filename (without extension): ")+ '.txt'
        filepath = os.path.join(path, filename)
        if os.path.exists(filepath):
            print(f"File already exists")
        else:
            return filename

if __name__ == "__main__":
    port = 'COM6'  
    baudrate = 115200

    visualizer = DataVisio(interval=5,max_points=1000)
    nano_ble = NanoBLE(port, baudrate)
    nano_ble.connect()

    print("Press Ctrl+C to stop reading data.")

    try:
        txt_filename = get_filename()
        ani = FuncAnimation(visualizer.fig, visualizer.update_plot, interval=1000)
        while nano_ble.connected:
            raw_data = nano_ble.read_data()
            if raw_data:
                formatted_data = nano_ble.format_data(raw_data)
                nano_ble.save_data_to_txt(formatted_data, txt_filename)
                numeric_data = [float(x.replace(',', '.')) for x in formatted_data.split(';')]
                print(f"Formatted data: {numeric_data}")
                visualizer.update_data(numeric_data)

            plt.pause(0.001)

    except KeyboardInterrupt:
        print("\nProgram interrupted by user.")
        visualizer.stop_visualization()
        nano_ble.disconnect()