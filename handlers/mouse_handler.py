"""
MouseHandler Class

This module defines the MouseHandler class that listens for mouse events 
(clicks, movements, and scrolls) and records them using an event handler. 
The class uses the pynput library to capture mouse events and the inspect 
module to retrieve information about the current execution context.
"""
from pynput import mouse
import inspect


class MouseHandler:
    def __init__(self, event_handler):
        self.listener = mouse.Listener(
            on_click=self.on_click, on_move=self.on_move, on_scroll=self.on_scroll)
        self.event_handler = event_handler

    def on_click(self, x, y, button, pressed):
        frame = inspect.currentframe()
        function_name = frame.f_code.co_name
        args, _, _, values = inspect.getargvalues(frame)
        self.event_handler.record(args[1:], values)

    def on_move(self, x, y):
        frame = inspect.currentframe()
        function_name = frame.f_code.co_name
        args, _, _, values = inspect.getargvalues(frame)
        self.event_handler.record(args[1:], values)

    def on_scroll(self, x, y, dx, dy):
        frame = inspect.currentframe()
        function_name = frame.f_code.co_name
        args, _, _, values = inspect.getargvalues(frame)
        self.event_handler.record(args[1:], values)

    def start(self):
        self.listener.start()

    def stop(self):
        self.listener.stop()
