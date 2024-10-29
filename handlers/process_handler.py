"""
ProcessHandler Module

This module defines the ProcessHandler class, which is responsible for monitoring the CPU usage of the currently active process. By running in a separate thread, it allows for real-time observation of process performance without disrupting the main application interface. The class emits updates via a PyQt signal, providing continuous feedback on CPU usage statistics, including average usage, peak usage, active process name, and elapsed time since monitoring began.

Class: ProcessHandler

- Inherits from: QThread - Facilitates concurrent execution and keeps the GUI responsive.
- Signal:
  - update_signal: Emits formatted CPU usage data to the main application.

Initialization

- __init__(self, frequency=1000, window_size=10): Initializes the process handler with specified sampling frequency and window size for moving average calculations.

Main Functionality

- run(self): Continuously monitors the CPU usage of the active process, updating metrics and emitting signals at defined intervals.
- stop(self): Safely terminates the monitoring thread.

Helper Functions

- get_active_process_id(): Retrieves the PID of the currently active window.
- get_active_process_name(pid): Returns the name of a process by its PID.
- get_cpu_times(pid): Obtains the total CPU time for the specified process.
- get_total_cpu_times(): Calculates total CPU times across all processes.
- calculate_cpu_usage(pid, initial_process_time, initial_total_time): Computes the CPU usage percentage for a given process based on initial and final CPU times.

"""

import win32process
import psutil
import win32gui
import time
from collections import deque
from PyQt5.QtCore import QObject, pyqtSignal, QThread


class ProcessHandler(QThread):
    # Signal to send updates to the main window
    update_signal = pyqtSignal(str)

    def __init__(self, frequency=1000, window_size=10):
        """
        Initializes the ProcessHandler.

        Args:
            frequency (int): Sampling frequency in milliseconds.
            window_size (int): Number of samples for the moving average.
        """
        super().__init__()
        self.frequency = 1.0 / frequency  # Convert to seconds
        self.window_size = window_size  # Number of samples for moving average
        self.usage_deque = deque(maxlen=window_size)
        self.active_pid = None
        self.running = True  # Controls the thread execution
        self.start_time = time.time()

    def run(self):
        """Monitor the CPU usage of the active process."""
        try:
            while self.running:
                pid = get_active_process_id()
                if pid:
                    if pid != self.active_pid:
                        # New process detected, update relevant data
                        self.active_pid = pid
                        self.initial_process_time = get_cpu_times(pid)
                        self.initial_total_time = get_total_cpu_times()
                        self.usage_deque.clear()  # Reset deque for new process

                    usage = calculate_cpu_usage(
                        pid, self.initial_process_time, self.initial_total_time)
                    self.usage_deque.append(usage)

                    if len(self.usage_deque) == self.window_size:
                        # Compute statistics
                        average_usage = sum(
                            self.usage_deque) / self.window_size
                        peak_usage = max(self.usage_deque)
                        elapsed_time = time.time() - self.start_time

                        # Format data and emit it via signal
                        event_data = (
                            f"Average CPU Usage: {average_usage:.2f}%\n"
                            f"Peak CPU Usage: {peak_usage:.2f}%\n"
                            f"Active Process: {get_active_process_name(pid)}\n"
                            f"Time Elapsed: {elapsed_time:.2f} seconds"
                        )

                        self.update_signal.emit(event_data)

                time.sleep(self.frequency)  # Control the sampling rate
        except Exception as e:
            print(f"Error in ProcessHandler: {e}")

    def stop(self):
        """Safely stop the thread."""
        self.running = False
        self.wait()  # Ensure the thread has finished


def get_active_process_id():
    """Retrieve the PID of the currently active window."""
    hwnd = win32gui.GetForegroundWindow()
    if hwnd:
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        return pid if pid > 0 else None
    return None


def get_active_process_name(pid):
    """Get the name of a process by PID.

    Args:
        pid (int): The process ID.

    Returns:
        str: The name of the process or "Unknown" if the process cannot be accessed.
    """
    try:
        return psutil.Process(pid).name()
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return "Unknown"


def get_cpu_times(pid):
    """Retrieve the total CPU time for a process.

    Args:
        pid (int): The process ID.

    Returns:
        float: The total CPU time in seconds or 0 if the process cannot be accessed.
    """
    try:
        process = psutil.Process(pid)
        cpu_times = process.cpu_times()
        return cpu_times.user + cpu_times.system
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return 0


def get_total_cpu_times():
    """Get total CPU times (user, system, idle, iowait).

    Returns:
        float: Total CPU times in seconds.
    """
    total_times = psutil.cpu_times()
    return sum(total_times[:4])  # User, system, idle, iowait


def calculate_cpu_usage(pid, initial_process_time, initial_total_time):
    """Calculate the CPU usage percentage for a process.

    Args:
        pid (int): The process ID.
        initial_process_time (float): Initial CPU time for the process.
        initial_total_time (float): Initial total CPU time.

    Returns:
        float: The CPU usage percentage.
    """
    final_process_time = get_cpu_times(pid)
    final_total_time = get_total_cpu_times()

    process_time_diff = final_process_time - initial_process_time
    total_time_diff = final_total_time - initial_total_time

    return (100 * process_time_diff / total_time_diff) if total_time_diff > 0 else 0
