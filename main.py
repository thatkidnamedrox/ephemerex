"""
Event Visualization Application

This application captures and visualizes user interactions, including mouse movements, 
click events, and key presses, in a 3D graph. It utilizes PyQt5 for the graphical user interface 
and matplotlib for plotting the data. The main features include:

- Recording mouse movements and clicks.
- Capturing keyboard events.
- Plotting the recorded data in a 3D space, showing the relationship between 
  mouse coordinates and the time elapsed.
- Calculating and displaying actions per minute (APM) based on the recorded events.

Modules:
- EventHandler, KeyboardHandler, MouseHandler, ProcessHandler: Custom modules for handling
  various user interactions.
- MainWindow: The main GUI window for the application.

Dependencies:
- PyQt5: For creating the GUI.
- pandas: For data manipulation and storage.
- matplotlib: For plotting the graphs.

Usage:
To run the application, execute the script. Upon closing the GUI, 
the recorded events will be processed, and visualizations will be displayed.
"""
import sys
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import QTimer

# Custom modules for event handling and GUI
from handlers import EventHandler, KeyboardHandler, MouseHandler, ProcessHandler, PlotHandler
from gui import MainWindow


if __name__ == "__main__":
    # Initialize the application and main window
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    # Create event handlers
    event_handler = EventHandler(window)

    keyboard_handler = KeyboardHandler(event_handler)
    keyboard_handler.update_signal.connect(
        window.worker.update_signal.emit)  # Connect signal
    keyboard_handler.start()

    mouse_handler = MouseHandler(event_handler)
    mouse_handler.start()

    process_handler = ProcessHandler()
    process_handler.update_signal.connect(
        window.worker.update_signal.emit)  # Connect signal
    process_handler.start()

    # Execute the application
    exit_code = app.exec_()

    csv_rows = "\n".join(window.csv_rows)
    header = "function_name,arguments,active_process,time_elapsed\n"
    csv_rows = header + csv_rows
    file_path = window.export_data(csv_rows, "log", "csv")

    # Load csv and plot graph
    # Doesn't actually play after the executable???
    # plot_handler = PlotHandler()
    # plot_handler.handle_csv(window)

    # Stop event handlers
    keyboard_handler.stop()
    mouse_handler.stop()
    process_handler.stop()

    # Ensure the application exits cleanly
    sys.exit(exit_code)
