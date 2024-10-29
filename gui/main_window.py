from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QWidget
from mpl_toolkits.mplot3d import Axes3D
import sys
import os
import time
import json
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QCheckBox,
    QLineEdit,
    QLabel,
    QApplication,
    QDialog,
    QComboBox,
    QFileDialog,
)

from PyQt5.QtGui import QIntValidator, QFont
from PyQt5.QtCore import Qt, QThread

from .helpers import Worker
from .dialogs import EditMetricsDialog, EditSettingsDialog
from .displays import DynamicTextDisplayApp

import sys
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib

matplotlib.use('Qt5Agg')  # Ensure Qt5 backend is used


class MainWindow(QWidget):
    SETTINGS_FILE = "app_settings.json"

    def __init__(self):
        super().__init__()

        # Remove the native title bar
        # self.setWindowFlags(Qt.FramelessWindowHint)

        # Set the fixed size of the window
        self.setFixedSize(400, 300)

        # Apply the dark theme stylesheet
        self.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                color: #f0f0f0;
                font-family: Arial;
                font-size: 18px;
            }
            QPushButton {
                background-color: #3c3f41;
                color: #ffffff;
                border: 1px solid #5c5c5c;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
            }
            QPushButton:pressed {
                background-color: #2e2e2e;
            }
            QCheckBox {
                spacing: 5px;
            }
            QLineEdit {
                background-color: #3c3f41;
                color: #ffffff;
                border: 1px solid #5c5c5c;
                border-radius: 3px;
                padding: 4px;
            }
        """)

        # Layout to hold everything, including the custom title bar
        self.layout = QVBoxLayout()
        # self.layout.setContentsMargins(0, 0, 0, 0)  # No extra margins

        # Create a custom title bar
        # self.init_title_bar()

        # Create the main content layout
        self.init_content()

        self.setLayout(self.layout)

        # Initialize states
        self.settings_states = {}
        self.dynamic_text_app = None
        self.metrics = {}
        self.metrics_states = {}
        self.csv_rows = []
        self.start_time = 0
        self.recording = True  # State for recording

        # Load saved settings
        self.load_settings()

        # Set default values
        self.output_directory = self.settings_states.get(
            "Set Output Directory", "./")
        self.send_osc = self.settings_states.get("Send OSC", True)
        self.osc_port = self.settings_states.get("Set OSC Port", 4560)
        self.osc_ip = self.settings_states.get("Set OSC IP", "127.0.0.1")
        self.user = self.settings_states.get("Set User", "n/a")
        # self.hotkey = self.settings_states.get("Set Hotkey", "F7")

        # Initialize worker thread
        self.init_worker()

    def set_title_bar_color(self):
        """Sets the custom title bar color using win32gui."""
        hwnd = self.winId()  # Get the window handle
        win32gui.SetClassLong(hwnd, win32con.GCL_HBRBACKGROUND,
                              win32gui.CreateSolidBrush(win32gui.RGB(0, 0, 0)))
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, win32gui.GetWindowLong(
            hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED)
        win32gui.SetLayeredWindowAttributes(
            hwnd, win32gui.RGB(0, 0, 0), 255, win32con.LWA_COLORKEY)

    def init_title_bar(self):
        """Creates a custom title bar with a black background and red text."""
        self.title_bar = QWidget()
        self.title_bar.setStyleSheet("background-color: black;")

        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(5, 0, 5, 0)

        # Title label
        self.title_label = QLabel("Metrics Dashboard")
        self.title_label.setStyleSheet("color: red; font-size: 16px;")
        self.title_label.setFont(QFont("Arial", 14))
        title_layout.addWidget(self.title_label)

        # Close button for the custom title bar
        self.close_button = QPushButton("X")
        self.close_button.setStyleSheet("""
            QPushButton {
                background-color: red;
                color: white;
                border: none;
                padding: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: darkred;
            }
        """)
        self.close_button.clicked.connect(self.close)
        title_layout.addWidget(self.close_button)

        self.title_bar.setLayout(title_layout)
        self.layout.addWidget(self.title_bar)

        # Enable dragging the window with the custom title bar
        self.title_bar.mousePressEvent = self.start_drag
        self.title_bar.mouseMoveEvent = self.do_drag

    def start_drag(self, event):
        """Stores the click position to move the window."""
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()

    def do_drag(self, event):
        """Moves the window as the mouse moves."""
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)

    def init_content(self):
        """Initializes the main content widgets."""
        # Edit Metrics Button
        self.edit_button = QPushButton("Edit Metrics")
        self.edit_button.clicked.connect(self.open_edit_metrics_dialog)
        self.layout.addWidget(self.edit_button)

        # Edit Settings Button
        self.edit_settings_button = QPushButton("Edit Settings")
        self.edit_settings_button.clicked.connect(
            self.open_edit_settings_dialog)
        self.layout.addWidget(self.edit_settings_button)

        # Start/Stop Recording Button
        self.record_button = QPushButton("Stop Recording")
        self.record_button.clicked.connect(self.toggle_recording)
        self.layout.addWidget(self.record_button)

        # Start/Stop Recording Button
        self.plot_button = QPushButton("Load Plot")
        self.plot_button.clicked.connect(self.open_plot_widget)
        self.layout.addWidget(self.plot_button)

        # Font Size Input
        self.font_size = QLineEdit(self)
        self.font_size.setValidator(QIntValidator())
        self.font_size.setPlaceholderText("Font Size")
        self.font_size.textChanged.connect(self.update_font_size)
        self.layout.addWidget(self.font_size)

        # Checkbox for Run Metrics
        self.run_metrics_checkbox = QCheckBox("Run Metrics")
        self.run_metrics_checkbox.stateChanged.connect(
            self.toggle_dynamic_text_app)
        self.layout.addWidget(self.run_metrics_checkbox)

    def toggle_recording(self):
        """Toggles the recording state and updates button text."""
        self.recording = not self.recording
        if self.recording:
            self.record_button.setText("Stop Recording")
        else:
            self.record_button.setText("Start Recording")

    def open_plot_widget(self):
        # load_csv()
        # handle_csv()
        file_path = self.browse_csv()
        self.handle_csv(file_path)
        print("Opened plot widget")
        pass

    def browse_csv(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load Plot")
        if file_path:
            return file_path

    def load_csv():
        pass

    def handle_csv(self, file_path):
        print(f"Number of entries: {len(self.csv_rows)}")

        # Prepare and export CSV data
        # csv_rows = "\n".join(self.csv_rows)
        # header = "function_name,arguments,active_process,time_elapsed\n"
        # csv_rows = header + csv_rows
        # file_path = self.export_data(csv_rows, "log", "csv")

        # Read the exported CSV file
        data = pd.read_csv(file_path)

        # Sort the DataFrame by 'time_elapsed' column in ascending order
        df_sorted = data.sort_values(by='time_elapsed')

        # Save the sorted DataFrame to a new CSV (optional)
        df_sorted.to_csv(file_path, index=False)

        # Plot graph
        self.plot_graph(df_sorted)

    def plot_graph(self, data):
        """Plot mouse movements, clicks, and key presses in a 3D graph.

        Args:
            data (pd.DataFrame): DataFrame containing the logged events.
        """
        print("Starting to plot graph...")  # Debug print

        # Filter data for different event types
        movement_data = data[data['function_name'] == 'on_move'].copy()
        click_data = data[data['function_name'].str.contains(
            'on_click')].copy()
        key_press_data = data[data['function_name'].str.contains(
            'on_press|on_release')].copy()

        # Create a 3D plot
        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(111, projection='3d')

        # Set dark background
        ax.set_facecolor('black')  # Background color of the plot
        fig.patch.set_facecolor('black')  # Figure background color

        # Plot mouse movements
        if not movement_data.empty:
            movement_data[['x', 'y']] = movement_data['arguments'].str.split(';', expand=True).apply(
                lambda col: col.str.split(':').str[1].astype(int))
            movement_data['time_elapsed'] = movement_data['time_elapsed'].astype(
                float)
            ax.plot(movement_data['x'], movement_data['y'], movement_data['time_elapsed'],
                    marker='o', markersize=3, linestyle='-', color='lime', alpha=0.6, label='Mouse Movement')

        # Plot click events
        if not click_data.empty:
            click_data[['x', 'y', 'button', 'pressed']] = click_data['arguments'].str.split(';', expand=True).apply(
                lambda col: col.str.split(':').str[1])
            click_data['time_elapsed'] = click_data['time_elapsed'].astype(
                float)
            click_data[['x', 'y']] = click_data[['x', 'y']].astype(int)
            ax.scatter(click_data['x'], click_data['y'], click_data['time_elapsed'],
                       marker='o', s=100, color='orange', alpha=0.8, label='Click Events')

        # Plot key presses
        if not key_press_data.empty:
            movement_data = movement_data.reset_index(drop=True)
            key_press_data = key_press_data.reset_index(drop=True)
            key_press_data[['x', 'y']] = movement_data[['x', 'y']
                                                       ].reindex(key_press_data.index, method='ffill')
            key_press_data['time_elapsed'] = key_press_data['time_elapsed'].astype(
                float)
            key_press_data['key'] = key_press_data['arguments'].str.split(';', expand=True).apply(
                lambda col: col.str.split(':').str[1].astype(str))

            for _, row in key_press_data.iterrows():
                ax.text(row['x'], row['y'], row['time_elapsed'], row['key'],
                        color='yellow', fontsize=8, ha='center', va='center')

        # Convert 'time_elapsed' to TimedeltaIndex for APM calculation
        all_events = data.copy()
        all_events['time_elapsed'] = pd.to_timedelta(
            all_events['time_elapsed'], unit='s')
        event_series = pd.Series(1, index=all_events['time_elapsed'])

        # Calculate Actions Per Minute (APM)
        rolling_counts = event_series.rolling(
            window='10s', min_periods=1).sum()
        apm = (rolling_counts / (10 / 60)).reset_index()
        apm.columns = ['time_elapsed', 'apm']

        # Add titles and labels to the 3D plot
        ax.set_title(
            'Mouse Movement, Click Events, and Key Presses Visualization (3D)', fontsize=20, color='white')
        ax.set_xlabel('X Coordinates', fontsize=14, color='white')
        ax.set_ylabel('Y Coordinates', fontsize=14, color='white')
        ax.set_zlabel('Time Elapsed (seconds)', fontsize=14, color='white')
        # Set pane background color to black
        ax.xaxis.set_pane_color((0, 0, 0, 1))
        ax.yaxis.set_pane_color((0, 0, 0, 1))
        ax.zaxis.set_pane_color((0, 0, 0, 1))
        ax.grid(color='white', linestyle='--', alpha=0.5)  # White grid lines

        # Add legend with white font
        legend = ax.legend(facecolor='black', edgecolor='white',
                           fontsize=12, loc='upper right')
        for text in legend.get_texts():
            text.set_color('white')  # Set legend text color to white

        # Plot APM (Actions Per Minute) with dark theme
        # Set window background to black
        plt.figure(figsize=(10, 6), facecolor='black')
        plt.plot(apm['time_elapsed'].dt.total_seconds(),
                 apm['apm'], label='APM', color='lime')
        plt.title('Actions Per Minute (APM)', fontsize=16, color='white')
        plt.xlabel('Time Elapsed (seconds)', fontsize=12, color='white')
        plt.ylabel('APM', fontsize=12, color='white')
        plt.gca().set_facecolor('black')  # Background color of the APM plot
        plt.grid(color='gray', alpha=0.5)  # Gray grid lines

        # Set axes ticks and labels color to white
        plt.gca().tick_params(axis='x', colors='white')  # X-axis ticks color
        plt.gca().tick_params(axis='y', colors='white')  # Y-axis ticks color
        plt.gca().tick_params(axis='both', which='both',
                              colors='white')  # Both axes ticks color

        # Add legend with white font
        legend = plt.legend(facecolor='black', edgecolor='white',
                            fontsize=12, loc='upper right')
        for text in legend.get_texts():
            text.set_color('white')  # Set legend text color to white

        # Display the plots
        plt.show()

    def update_font_size(self):
        """Updates the font size of the dynamic text display."""
        font_size = self.font_size.text()
        if font_size == "":
            return
        if self.dynamic_text_app:
            self.dynamic_text_app.adjust_font_size(int(font_size))
        # Save font size to state
        self.settings_states["Font Size"] = font_size
        self.save_settings()

    def open_edit_metrics_dialog(self):
        """Opens a dialog to edit metrics settings."""
        dialog = EditMetricsDialog(self, self.metrics_states)
        dialog.exec_()
        self.metrics_states.update(dialog.get_checkbox_states())
        self.save_settings()

    def open_edit_settings_dialog(self):
        """Opens a dialog to edit application settings."""
        dialog = EditSettingsDialog(self, self.settings_states)
        dialog.exec_()
        self.settings_states.update(dialog.get_checkbox_states())
        self.save_settings()

        self.output_directory = self.settings_states.get(
            "Set Output Directory", "./")
        self.metrics["Output Directory"] = self.output_directory
        self.append_log(f"Output Directory: {self.output_directory}")

        self.user = self.settings_states.get("Set User", "n/a")
        self.metrics["User"] = self.user
        self.append_log(f"User: {self.user}")

        self.send_osc = self.settings_states.get("Send OSC", True)
        self.osc_port = self.settings_states.get("Set OSC Port", 4560)
        self.osc_ip = self.settings_states.get("Set OSC IP", "127.0.0.1")
        # self.hotkey = self.settings_states.get("Set Hotkey", "F7")

    def toggle_dynamic_text_app(self, state):
        """Toggles the visibility of the dynamic text display application."""
        if state == Qt.Checked:
            if not self.dynamic_text_app:
                self.dynamic_text_app = DynamicTextDisplayApp()
                self.update_font_size()
                self.dynamic_text_app.show()
        else:
            if self.dynamic_text_app:
                self.dynamic_text_app.close()
                self.dynamic_text_app = None

        self.settings_states["Run Metrics"] = state == Qt.Checked
        self.save_settings()

    def save_settings(self):
        """Saves the current settings to a JSON file."""
        new_settings = {
            "font_size": self.font_size.text(),
            "run_metrics": self.run_metrics_checkbox.isChecked(),
            "metrics_states": self.metrics_states,
            "settings_states": self.settings_states,
        }

        # Load existing settings if the file exists
        try:
            if os.path.exists(self.SETTINGS_FILE):
                with open(self.SETTINGS_FILE, "r") as f:
                    existing_settings = json.load(f)
            else:
                existing_settings = {}
        except json.JSONDecodeError:
            existing_settings = {}  # Handle corrupt or invalid JSON

        # Merge the new settings with the existing ones
        merged_settings = self.deep_merge_dicts(
            existing_settings, new_settings)

        # Save the merged settings back to the file
        with open(self.SETTINGS_FILE, "w") as f:
            json.dump(merged_settings, f, indent=4)

    def deep_merge_dicts(self, target, source):
        """Recursively merges two dictionaries, giving priority to the source."""
        for key, value in source.items():
            if isinstance(value, dict) and key in target:
                target[key] = self.deep_merge_dicts(target[key], value)
            else:
                target[key] = value
        return target

    def load_settings(self):
        """Loads settings from the JSON file, if it exists."""
        if os.path.exists(self.SETTINGS_FILE):
            try:
                with open(self.SETTINGS_FILE, "r") as f:
                    settings = json.load(f)

                    # Load values into the application state
                    self.font_size.setText(settings.get("font_size", ""))
                    self.run_metrics_checkbox.setChecked(
                        settings.get("run_metrics", False)
                    )
                    self.metrics_states = settings.get("metrics_states", {})
                    self.settings_states = settings.get("settings_states", {})

                    # Ensure "Output Directory" is properly loaded
                    self.output_directory = self.settings_states.get(
                        "Set Output Directory", "./")
                    self.metrics["Output Directory"] = self.output_directory

                    self.user = self.settings_states.get("Set User", "n/a")
                    self.metrics["User"] = self.user
            except json.JSONDecodeError:
                print("Failed to load settings: Invalid JSON format.")

    def append_log(self, message):
        """Appends log messages and updates the dynamic text display."""
        lines = message.split('\n')
        msg = ""
        for line in lines:
            if not line.strip():  # Skip empty lines
                continue
            label, value = line.split(': ', 1) if ': ' in line else (line, '')

            if label == "Text":
                self.export_data(message, "run", "txt")
            elif label == "Start":
                self.start_time = float(value)
            else:
                self.metrics[label] = value

            if label == "OSC" and self.recording:  # Only append if recording
                self.csv_rows.append(value)

        if self.dynamic_text_app:
            for label, shown in self.metrics_states.items():
                if shown:
                    value = self.metrics.get(label, "n/a")
                    msg += f"{label}: {value}\n"
            if msg:
                self.dynamic_text_app.set_text(msg)

    def init_worker(self):
        """Initializes the worker thread for background processing."""
        self.worker_thread = QThread()
        self.worker = Worker()

        # Connect signals and move worker to thread
        self.worker.update_signal.connect(self.append_log)
        self.worker.moveToThread(self.worker_thread)

        # Ensure the worker thread stops properly
        self.worker_thread.finished.connect(self.worker.deleteLater)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)

        self.worker_thread.start()

    def export_data(self, data, filename_prefix="run", file_extension="txt", include_timestamp=True):
        """Exports data to a file with an optional timestamp."""
        time_elapsed = time.time() - self.start_time
        timestamp = time.strftime("%Y%m%d_%H%M%S") if include_timestamp else ""
        filename = f"{filename_prefix}_{timestamp}.{file_extension}" if timestamp else f"{filename_prefix}.{file_extension}"
        output_directory = self.metrics.get("Output Directory", "./")
        file_path = os.path.join(output_directory, filename)

        try:
            with open(file_path, "w", encoding="utf-8", newline='') as file:
                if isinstance(data, (dict, list)):
                    file.write(json.dumps(data, indent=4))
                else:
                    file.write(data)

            print(f"Data saved to {file_path}")
            if file_extension == "txt":
                active_process = self.metrics["Active Process"]
                self.append_log(
                    f"OSC: on_run,path:{filename},{active_process},{time_elapsed}")
            return file_path

        except IOError as error:
            print(f"Error saving data to {file_path}: {error}")
            return None


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
