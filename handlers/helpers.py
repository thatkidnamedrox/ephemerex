from PyQt5.QtCore import QObject, pyqtSignal
import time
import sys
from collections import deque
import platform
import re
import win32gui
import psutil
import win32process


def sanitize_filename(filename):
    """Sanitize a filename by replacing invalid characters."""
    return re.sub(r"[^a-zA-Z0-9_\-\.]", "_", filename)


def retrieve_active_window_info():
    hwnd = win32gui.GetForegroundWindow()
    title = win32gui.GetWindowText(hwnd)
    _, pid = win32process.GetWindowThreadProcessId(hwnd)
    if pid < 0:
        return False
    try:
        process = psutil.Process(pid)
        result = {
            "hwnd": hwnd,
            "title": title,
            "pid": pid,
            "process": process
        }
        return result
    except psutil.NoSuchProcess:
        print("Error caught.")
        return False
    else:
        "Something still went wrong :()"


def get_active_process_id():
    hwnd = win32gui.GetForegroundWindow()
    if hwnd:  # Ensure the window handle is valid
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        if pid > 0:  # Ensure the pid is a valid positive integer
            return pid
    return None


def get_active_process_name(pid):
    try:
        process = psutil.Process(pid)
        return process.name()
    except psutil.NoSuchProcess:
        return "Unknown"


def get_cpu_times(pid):
    try:
        process = psutil.Process(pid)
        cpu_times = process.cpu_times()
        return cpu_times.user + cpu_times.system
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        return 0


def get_total_cpu_times():
    total_times = psutil.cpu_times()
    # sum user, system, idle, iowait (first four fields)
    return sum(total_times[:4])


def calculate_cpu_usage(pid, initial_process_time, initial_total_time):
    # Get final times
    final_process_time = get_cpu_times(pid)
    final_total_time = get_total_cpu_times()

    # Calculate the differences
    process_time_diff = final_process_time - initial_process_time
    total_time_diff = final_total_time - initial_total_time

    # Calculate CPU usage as a percentage
    cpu_usage = 100 * process_time_diff / \
        total_time_diff if total_time_diff > 0 else 0
    return cpu_usage


def monitor_cpu_usage(frequency=1000, duration=60, window_size=10):
    usage_deque = deque(maxlen=window_size)
    total_usage = 0
    count = 0

    current_pid = get_active_process_id()
    if current_pid:
        current_process_name = get_active_process_name(current_pid)
        initial_process_time = get_cpu_times(current_pid)
        initial_total_time = get_total_cpu_times()
    else:
        print("Could not retrieve a valid process ID.")
        return
    try:
        while True:
            new_pid = get_active_process_id()
            if new_pid and new_pid != current_pid:
                # Update process ID and initial times
                current_pid = new_pid
                current_process_name = get_active_process_name(current_pid)
                initial_process_time = get_cpu_times(current_pid)
                initial_total_time = get_total_cpu_times()
                usage_deque.clear()  # Clear the deque for the new process

            if current_pid:
                usage = calculate_cpu_usage(
                    current_pid, initial_process_time, initial_total_time)
                usage_deque.append(usage)
                total_usage += usage
                count += 1

                # Calculate peak usage for the last `window_size` iterations
                peak_usage = max(usage_deque) if usage_deque else 0

                # Print current stats
                if count % 10 == 0:  # Print every 10 samples for readability
                    average_usage = sum(usage_deque)/window_size
                    print(
                        f"avg:{average_usage},peak:{peak_usage},process:{get_active_process_name(current_pid)}")

            time.sleep(1 / frequency)
    except Exception as e:
        print(e)


class Worker(QObject):
    update_signal = pyqtSignal(str)

    def process(self, message):
        # Perform the intended work here
        print(f"Processing: {message}")
        self.update_signal.emit(f"Processed: {message}")
