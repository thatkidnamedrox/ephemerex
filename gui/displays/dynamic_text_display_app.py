"""
DynamicTextDisplayApp Module

This module defines the DynamicTextDisplayApp class, which creates a
transparent, draggable window displaying dynamic text. The text can be
customized, and the window will adjust its size based on the content.
"""

from PyQt5.QtGui import QFont, QFontMetrics
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtWidgets import QApplication, QLabel, QWidget
import sys


class DynamicTextDisplayApp(QWidget):
    def __init__(self, parent=None, font_size=24):
        """
        Initializes the DynamicTextDisplayApp.

        Args:
            parent (QWidget): Parent widget, if any.
            font_size (int): Initial font size for the displayed text.
        """
        super().__init__(parent)

        # Set initial window flags and attributes
        self.setWindowFlags(Qt.FramelessWindowHint |
                            Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Enable mouse tracking
        self.setMouseTracking(True)

        # Initialize dragging state and position
        self.dragging = False
        self.drag_position = QPoint()

        # Create the label to display text
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        # Set a default font
        self.font = QFont("Arial", font_size)
        self.label.setFont(self.font)

        # Initialize text with default content
        self.set_text("Hello World", "white")

    def adjust_font_size(self, font_size=24):
        """Adjusts the font size of the displayed text."""
        self.font = QFont("Arial", font_size)
        self.label.setFont(self.font)
        self.adjust_window_size()

    def set_text(self, text, color="white"):
        """Updates the displayed text and resizes the window to fit the content.

        Args:
            text (str): The text to display.
            color (str): The text color.
        """
        self.label.setText(text)
        self.label.setStyleSheet(
            f"color: {color}; background-color: transparent;")
        self.adjust_window_size()

    def adjust_window_size(self):
        """Adjusts the window size based on the content and font size."""
        font_metrics = QFontMetrics(self.label.font())

        # Retrieve the text and split it into lines
        text_lines = self.label.text().splitlines()
        if text_lines and text_lines[-1] == "":
            text_lines = text_lines[:-1]
        num_lines = len(text_lines) if text_lines else 1
        # Calculate the maximum width and height for all lines
        text_width = font_metrics.horizontalAdvance(
            max(text_lines, key=len)) + 40  # Add padding
        text_height = (font_metrics.height() + 40) * num_lines  # Add padding

        # Update the label geometry and window size
        self.label.setGeometry(0, 0, text_width, text_height)
        self.setFixedSize(text_width, text_height)

    def mousePressEvent(self, event):
        """Tracks the start of a drag operation."""
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        """Moves the window during a drag operation."""
        if self.dragging:
            self.move(event.globalPos() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        """Ends the drag operation."""
        if event.button() == Qt.LeftButton:
            self.dragging = False
            event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DynamicTextDisplayApp()
    window.show()
    sys.exit(app.exec_())
