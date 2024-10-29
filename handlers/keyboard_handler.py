"""
KeyboardHandler Module

This module handles keyboard events using the `pynput` library, processes hotkeys,
and manages text caching from the active window. It uses PyQt5 signals to communicate
events to a main application. The module includes functions for copying text from
the active window and exporting data to files.

Classes:
- KeyboardHandler: Inherits from QThread and handles keyboard events.
Functions:
- press_hotkeys: Executes a series of hotkeys using `pyautogui`.
- copy_text_from_active_window: Simulates a copy-paste operation from the active window.
- copy_file_to_clipboard: Copies the contents of a specified file to the clipboard.
- export_data: Saves data to a file with a specified filename prefix and extension.
"""

from pynput import keyboard
import inspect
import pyautogui
import platform
import win32gui
import pyperclip
import time
import os
from PyQt5.QtCore import QObject, pyqtSignal, QThread


class KeyboardHandler(QThread):
    update_signal = pyqtSignal(str)

    def __init__(self, event_handler):
        """Initialize the KeyboardHandler with an event handler."""
        super().__init__()
        self.listener = keyboard.Listener(
            on_press=self.on_press, on_release=self.on_release)
        self.num_keyboard_events = 0
        self.total_num_keyboard_events = 0
        self.pressed_keys = []
        self.event_handler = event_handler
        self.history = []
        self.cached_text = 0
        self.key_states = {}
        self.copy_text = False
        self.listener_active_press = True
        self.listener_active_release = True

        self.copy_text_presses = 0
        self.copy_text_releases = 0

    def on_press(self, key):
        """Handle key press events."""
        frame = inspect.currentframe()
        function_name = frame.f_code.co_name
        args, _, _, values = inspect.getargvalues(frame)

        if not self.listener_active_press:
            self.copy_text_presses += 1
            if self.copy_text_presses == 4:
                self.listener_active_press = True
                self.copy_text_presses = 0
            return

        if key not in self.key_states:
            self.key_states[key] = time.time()
            self.pressed_keys.append(key)
            line = f"Pressed Keys: {self.pressed_keys}"
            self.update_signal.emit(line)
        else:
            self.on_hold(key)

        self.event_handler.record(args[1:], values)
        self.num_keyboard_events += 1
        self.total_num_keyboard_events += 1
        self.process(key)

    def on_hold(self, key):
        """Handle keys that are held down."""
        press_time = self.key_states[key]
        held_duration = time.time() - press_time

    def on_release(self, key):
        """Handle key release events."""
        frame = inspect.currentframe()
        function_name = frame.f_code.co_name
        args, _, _, values = inspect.getargvalues(frame)

        if not self.listener_active_release and key != keyboard.Key.f7:
            self.copy_text_releases += 1
            if self.copy_text_releases == 4:
                self.listener_active = True
                self.copy_text_releases = 0
            return

        if len(self.pressed_keys) > 1 and self.pressed_keys[0] == keyboard.Key.shift_l:
            num_texts = len(self.history)
            if num_texts > 0:
                if self.pressed_keys[1] == keyboard.Key.left:
                    self.cached_text = (self.cached_text - 1) % num_texts
                    file = self.history[self.cached_text]
                    pyperclip.copy(file)
                    self.update_signal.emit(f"Cached Text: {file}")
                    self.update_signal.emit(f"Snippet: {self.cached_text}")
                elif self.pressed_keys[1] == keyboard.Key.right:
                    self.cached_text = (self.cached_text + 1) % num_texts
                    file = self.history[self.cached_text]
                    pyperclip.copy(file)
                    self.update_signal.emit(f"Cached Text: {file}")
                    self.update_signal.emit(f"Snippet: {self.cached_text}")

        if key in self.key_states:
            press_time = self.key_states.pop(key)
            self.pressed_keys.remove(key)
            line = f"Pressed Keys: {self.pressed_keys}"
            self.update_signal.emit(line)

        self.event_handler.record(args[1:], values)

    def start(self):
        """Start the keyboard listener."""
        self.listener.start()

    def stop(self):
        """Stop the keyboard listener."""
        self.listener.stop()

    def process(self, key):
        """Process specific key actions."""
        if key == keyboard.Key.f7:
            self.listener_active_release = False
            self.listener_active_press = False
            print("listener paused")
            # self.num_keyboard_events = -6
            text = copy_text_from_active_window()
            if text:
                self.history.append(text)
                self.cached_text = len(self.history) - 1
                self.update_signal.emit(f"Text: {text}")
                self.update_signal.emit(f"Cached Text: {self.cached_text}")
                self.update_signal.emit(
                    f"Number of Snippets: {len(self.history)}")


def press_hotkeys(*keys):
    """Execute a series of hotkeys using pyautogui."""
    for key in keys:
        pyautogui.hotkey(*key)


def copy_text_from_active_window():
    """Get the text from the active window, simulating a copy-paste operation."""
    if platform.system() == "Windows":
        hwnd = win32gui.GetForegroundWindow()
        if hwnd:
            win32gui.SetForegroundWindow(hwnd)
            if win32gui.GetWindowText(hwnd) == "Sonic Pi":
                press_hotkeys(["alt", "a"], ["alt", "c"])
            else:
                press_hotkeys(["ctrl", "a"], ["ctrl", "c"])
            pyautogui.click()
            return pyperclip.paste()
    return None


def copy_file_to_clipboard(file_path):
    """Copy the content of a specified file to the clipboard."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        pyperclip.copy(content)
        print("Content copied to clipboard successfully!")
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")


def export_data(data, filename_prefix="data", file_extension="txt", include_timestamp=True):
    """Save data to a file with specified filename prefix and extension."""
    timestamp = time.strftime("%Y%m%d_%H%M%S") if include_timestamp else ""
    filename = f"{filename_prefix}_{timestamp}.{file_extension}" if timestamp else f"{filename_prefix}.{file_extension}"
    file_path = os.path.join("./", filename)
    try:
        with open(file_path, "w", encoding="utf-8", newline='') as file:
            if isinstance(data, (dict, list)):
                file.write(json.dumps(data, indent=4))
            else:
                file.write(data)
        print(f"Data saved to {file_path}")
        return file_path
    except IOError as error:
        print(f"Error saving data to {file_path}: {error}")
        return None
