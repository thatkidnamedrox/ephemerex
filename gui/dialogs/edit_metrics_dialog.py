"""
EditMetricsDialog Module

This module defines the EditMetricsDialog class, which provides a dialog 
for configuring various metrics through checkboxes. The dialog includes 
sections for input, performance, output, and user information metrics.
"""

from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QCheckBox,
    QPushButton,
)
from PyQt5.QtCore import Qt


class EditMetricsDialog(QDialog):
    def __init__(self, parent=None, checkbox_states=None):
        """
        Initializes the EditMetricsDialog.

        Args:
            parent (QWidget): Parent widget, if any.
            checkbox_states (dict): Dictionary containing initial checkbox states.
        """
        super().__init__(parent)

        self.setWindowTitle("Edit Metrics")
        self.setGeometry(150, 150, 400, 500)

        layout = QVBoxLayout()

        # Input Metrics
        layout.addWidget(QLabel("Input Metrics"))
        self.input_metrics_checkboxes = self._create_input_metrics_checkboxes()
        self._set_checkbox_states(
            self.input_metrics_checkboxes, checkbox_states)
        self._add_checkboxes_to_layout(self.input_metrics_checkboxes, layout)

        # Performance Metrics
        layout.addWidget(QLabel("Performance Metrics"))
        self.performance_metrics_checkboxes = self._create_performance_metrics_checkboxes()
        self._set_checkbox_states(
            self.performance_metrics_checkboxes, checkbox_states)
        self._add_checkboxes_to_layout(
            self.performance_metrics_checkboxes, layout)

        # Output Metrics
        layout.addWidget(QLabel("Output Metrics"))
        self.output_metrics_checkboxes = self._create_output_metrics_checkboxes()
        self._set_checkbox_states(
            self.output_metrics_checkboxes, checkbox_states)
        self._add_checkboxes_to_layout(self.output_metrics_checkboxes, layout)

        # User Information
        layout.addWidget(QLabel("User Information"))
        self.user_information_checkboxes = self._create_user_information_checkboxes()
        self._set_checkbox_states(
            self.user_information_checkboxes, checkbox_states)
        self._add_checkboxes_to_layout(
            self.user_information_checkboxes, layout)

        # Close Button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)

        self.setLayout(layout)

    def _create_input_metrics_checkboxes(self):
        """Creates and returns a list of input metrics checkboxes."""
        return [
            QCheckBox("Mouse Position"),
            # QCheckBox("Mouse X"),
            # QCheckBox("Mouse Y"),
            # QCheckBox("Mouse Movement"),
            # QCheckBox("Mouse ΔX (dx)"),
            # QCheckBox("Mouse ΔY (dy)"),
            QCheckBox("Mouse Speed"),
            QLabel("Keyboard Input"),
            QCheckBox("Pressed Keys"),
            QCheckBox("Number of Keypresses"),
            QCheckBox("Typing Speed"),
            # QCheckBox("Shortcuts Used"),
        ]

    def _create_performance_metrics_checkboxes(self):
        """Creates and returns a list of performance metrics checkboxes."""
        return [
            # QCheckBox("Current Process Information"),
            QCheckBox("Active Process"),
            # QCheckBox("CPU Usage"),
            # QCheckBox("Current CPU Usage"),
            QCheckBox("Average CPU Usage"),
            QCheckBox("Peak CPU Usage"),
            # QCheckBox("Memory Usage"),
            # QCheckBox("Current Memory Usage"),
            # QCheckBox("Peak Memory Usage"),
        ]

    def _create_output_metrics_checkboxes(self):
        """Creates and returns a list of output metrics checkboxes."""
        return [
            QCheckBox("Output Directory"),
            QCheckBox("Time Elapsed"),
            # QCheckBox("History Selector"),
            # QCheckBox("Number of Mouse Events"),
            QCheckBox("OSC"),
        ]

    def _create_user_information_checkboxes(self):
        """Creates and returns a list of user information checkboxes."""
        return [
            QCheckBox("User"),
        ]

    def _set_checkbox_states(self, checkboxes, states):
        """Sets the states of checkboxes based on provided states.

        Args:
            checkboxes (list): List of checkboxes to set states for.
            states (dict): Dictionary containing checkbox states.
        """
        if states:
            for checkbox in checkboxes:
                if isinstance(checkbox, QCheckBox):
                    checkbox.setChecked(states.get(checkbox.text(), False))

    def _add_checkboxes_to_layout(self, checkboxes, layout):
        """Adds a list of checkboxes to the specified layout.

        Args:
            checkboxes (list): List of checkboxes to add.
            layout (QLayout): The layout to add checkboxes to.
        """
        for checkbox in checkboxes:
            layout.addWidget(checkbox)

    def get_checkbox_states(self):
        """Returns the states of all checkboxes in the dialog."""
        states = {}
        all_checkboxes = (
            self.input_metrics_checkboxes +
            self.performance_metrics_checkboxes +
            self.output_metrics_checkboxes +
            self.user_information_checkboxes
        )
        for checkbox in all_checkboxes:
            if isinstance(checkbox, QCheckBox):
                states[checkbox.text()] = checkbox.isChecked()
        return states
