"""
Event Handler for User Interactions

This script defines an EventHandler class that captures user interactions such as mouse movements, 
clicks, and keyboard presses. It calculates statistics related to these events and sends 
Open Sound Control (OSC) messages for real-time monitoring or further processing. 

Key Features:
- Tracks mouse movements and calculates the change in position.
- Records keyboard presses and calculates typing speed (WPM).
- Sends event data as OSC messages to a specified address.
- Logs active window information for context on user interactions.

Dependencies:
- pyautogui: For controlling the mouse and retrieving information.
- pythonosc: For sending OSC messages.
- collections: For utilizing defaultdict for event counts.
- helpers: Custom helper functions for sanitizing filenames and retrieving active window information.
"""

import time
import pyautogui
from collections import defaultdict
from pythonosc import udp_client  # Import OSC client

# Custom modules for helper functions
from .helpers import sanitize_filename, retrieve_active_window_info


class EventHandler:
    def __init__(self, main_window, osc_ip="127.0.0.1", osc_port=4560):
        """Initialize the EventHandler.

        Args:
            main_window: Reference to the main application window.
            osc_ip (str): IP address for the OSC client. Default is localhost.
            osc_port (int): Port number for the OSC client. Default is 4560.
        """
        self.start_time = time.time()

        self.key_shortcut_counts = {}
        self.current_active_window_title = ""
        self.active_process = None
        self.saved_filenames = []
        self.saved_timestamps = []
        self.event_statistics = {}
        self.output_directory = ""
        self.logging_enabled = True
        self.active_window = None
        self.hwnd = None
        self.event_counts = defaultdict(int)
        self.pid = None
        self.registered_windows = []
        self.num_focus_shifts = 0
        self.process = None
        self.num_key_presses = 0

        self.keypress_timestamps = []  # Track timestamps for WPM calculation
        self.prev_mouse_x = None  # Previous mouse X-coordinate
        self.prev_mouse_y = None  # Previous mouse Y-coordinate

        active_window_info = retrieve_active_window_info()
        self.process = active_window_info["process"]
        self.pid = active_window_info["pid"]
        self.main_window = main_window

        self.main_window.worker.update_signal.emit(f"Start: {self.start_time}")

        # OSC Client Setup
        self.osc_ip = str(self.main_window.osc_ip)
        self.osc_port = int(self.main_window.osc_port)
        self.osc_client = udp_client.SimpleUDPClient(
            self.osc_ip, self.osc_port)

        # self.hotkey = "F7"

    def send_osc_message(self, address, message):
        """Send an OSC message to the specified address.

        Args:
            address (str): The OSC address to send the message to.
            message: The message content to be sent.
        """
        try:
            self.osc_client.send_message(address, message)
        except Exception as e:
            print(f"Failed to send OSC message: {e}")

    def calculate_typing_speed(self):
        """Calculate typing speed in words per minute (WPM).

        Returns:
            float: The calculated typing speed in WPM.
        """
        if len(self.keypress_timestamps) < 2:
            return 0  # Not enough data to calculate WPM

        # In seconds
        elapsed_time = self.keypress_timestamps[-1] - \
            self.keypress_timestamps[0]
        # Average word length assumed to be 5 characters
        words_typed = self.num_key_presses / 5
        wpm = (words_typed / elapsed_time) * 60  # Convert to WPM
        return round(wpm, 2)

    def calculate_mouse_movement(self, x, y):
        """Calculate the change in mouse position since the last recorded position.

        Args:
            x (int): Current mouse X-coordinate.
            y (int): Current mouse Y-coordinate.

        Returns:
            tuple: Change in mouse position (dx, dy).
        """
        if self.prev_mouse_x is None or self.prev_mouse_y is None:
            self.prev_mouse_x, self.prev_mouse_y = x, y
            return 0, 0  # No previous data to compare with

        dx = x - self.prev_mouse_x
        dy = y - self.prev_mouse_y

        # Update previous coordinates
        self.prev_mouse_x, self.prev_mouse_y = x, y
        return dx, dy

    def record(self, args, values):
        """Record user events and send OSC messages with relevant data.

        Args:
            args (list): List of expected argument names.
            values (dict): Dictionary containing event data.
        """
        if not self.logging_enabled:
            return

        event_time = time.time() - self.start_time
        active_window_info = retrieve_active_window_info()

        if active_window_info:
            self.process = active_window_info["process"]
            self.pid = active_window_info["pid"]

        active_process_name = self.process.name()
        function_name = values["function_name"]

        # Format arguments for logging
        arguments = ';'.join(
            f"{k}:{v}" if ',' not in str(v) else f"\"{k}:{v}\""
            for k, v in values.items() if k in args
        )

        event_entry = f"{function_name},{arguments},{active_process_name},{event_time}"
        osc_address = f"/event"
        osc_message = event_entry.split(",")

        if (str(self.main_window.osc_ip) != self.osc_ip or int(self.main_window.osc_port) != self.osc_port):
            self.osc_port = int(self.main_window.osc_port)
            self.osc_ip = str(self.main_window.osc_ip)
            self.osc_client = udp_client.SimpleUDPClient(
                self.osc_ip, self.osc_port)

        if (self.main_window.send_osc):
            self.send_osc_message(osc_address, osc_message)

        # if (self.main_window.hotkey != self.hotkey):
        #     self.hotkey = self.main_window.hotkey

        event_data = {
            "OSC": event_entry.strip(),
        }

        # Process mouse movement events
        if function_name == "on_move":
            x, y = values["x"], values["y"]
            dx, dy = self.calculate_mouse_movement(x, y)  # Calculate dx, dy

            event_data["Mouse X"] = x
            event_data["Mouse Y"] = y
            event_data.update({
                "Mouse Position": f"({x},{y})",
                "Mouse ΔX (dx)": dx,
                "Mouse ΔY (dy)": dy,
                "Mouse Speed": f"({dx},{dy})"
            })

        # Process keyboard press events
        if function_name == "on_press":
            self.num_key_presses += 1
            self.keypress_timestamps.append(time.time())  # Record timestamp

            # Calculate typing speed (WPM)
            wpm = self.calculate_typing_speed()

            event_data.update({
                "Number of Keypresses": self.num_key_presses,
                "Typing Speed": wpm,
            })

        # Prepare data for updating the main window
        lines = "\n".join(f"{key}: {event_data[key]}" for key in event_data)
        self.main_window.worker.update_signal.emit(lines)
