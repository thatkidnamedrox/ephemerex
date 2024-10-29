"""
EditSettingsDialog Module

This module contains the EditSettingsDialog class, which provides a user interface
for editing application settings. The dialog allows users to specify output 
directories, configuration files, user settings, audio input/output options, 
and various preferences. The settings are organized in a clear layout with 
input fields, combo boxes, and checkboxes, enabling easy configuration.

Key Features:
- Input fields for output directories and configuration files with browse buttons.
- Text inputs for user-specific settings and history navigation.
- Combo boxes for selecting audio input and output options.
- Checkboxes for enabling various features such as filestamps and analytics.
- Functionality to retrieve the current states of the settings.

Dependencies:
- PyQt5: Required for creating the GUI components.

Usage:
- Instantiate the EditSettingsDialog class with an optional parent and a dictionary
  containing initial checkbox states.
- Call the exec_() method to display the dialog.
- After the dialog is closed, use the get_checkbox_states() method to retrieve 
  the updated settings.
"""

import sys
from PyQt5.QtWidgets import (
    QApplication,
    QDialog,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QCheckBox,
    QComboBox,
    QPushButton,
    QFileDialog,
    QHBoxLayout
)


class EditSettingsDialog(QDialog):
    def __init__(self, parent=None, checkbox_states=None):
        """
        Initializes the EditSettingsDialog.

        Args:
            parent (QWidget, optional): The parent widget for the dialog.
            checkbox_states (dict, optional): A dictionary holding initial states
                                               for the settings inputs.
        """
        super().__init__(parent)
        self.setWindowTitle("Edit Settings")
        self.setGeometry(150, 150, 400, 500)

        self.checkbox_states = checkbox_states or {}
        layout = QVBoxLayout()

        # Create input fields and checkboxes
        self.output_directory_input = self.create_browse_input(
            layout, "Set Output Directory", self.browse_output_directory
        )

        self.set_osc_ip_input = self.create_text_input(
            layout, "Set OSC IP")

        self.set_osc_ip_input.setText("127.0.0.1")

        self.set_osc_port_input = self.create_text_input(
            layout, "Set OSC Port")

        self.send_osc_checkbox = self.create_checkbox(
            layout, "Send OSC")

        # self.config_file_input = self.create_browse_input(
        #     layout, "Set Configuration File", self.browse_config_file
        # )

        self.user_input = self.create_text_input(layout, "Set User")
        # self.hotkey = self.create_text_input(layout, "Set Hotkey")
        # self.history_navigation_input = self.create_text_input(
        #     layout, "Set History Navigation")
        # self.history_selector_input = self.create_text_input(
        #     layout, "Set History Selector")
        # self.sensitivity_input = self.create_text_input(
        #     layout, "Set Sensitivity")

        # self.audio_input_selector = self.create_combo_input(
        #     layout, "Set Audio Input", ["Mic 1", "Mic 2", "Line In"]
        # )
        # self.audio_output_selector = self.create_combo_input(
        #     layout, "Set Audio Output", ["Speakers", "Headphones", "Line Out"]
        # )

        # self.filestamps_checkbox = self.create_checkbox(
        #     layout, "Enable Filestamps")
        # self.analytics_checkbox = self.create_checkbox(
        #     layout, "Enable Post-Performance Analytics")
        # self.always_on_top_checkbox = self.create_checkbox(
        #     layout, "Set Always on Top")

        # Close Button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)

        self.setLayout(layout)

    def create_browse_input(self, layout, label_text, browse_func):
        """Create a label, QLineEdit, and browse button for directory/file input."""
        layout.addWidget(QLabel(label_text))
        input_layout = QHBoxLayout()

        input_field = QLineEdit()
        input_field.setText(self.checkbox_states.get(label_text, ""))
        input_layout.addWidget(input_field)

        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(browse_func)
        input_layout.addWidget(browse_button)

        layout.addLayout(input_layout)
        return input_field

    def create_text_input(self, layout, label_text):
        """Create a label and QLineEdit for text input."""
        layout.addWidget(QLabel(label_text))
        input_field = QLineEdit()
        input_field.setText(self.checkbox_states.get(label_text, ""))
        layout.addWidget(input_field)
        return input_field

    def create_combo_input(self, layout, label_text, options):
        """Create a label and QComboBox for selection input."""
        layout.addWidget(QLabel(label_text))
        combo_box = QComboBox()
        combo_box.addItems(options)
        combo_box.setCurrentText(
            self.checkbox_states.get(label_text, options[0]))
        layout.addWidget(combo_box)
        return combo_box

    def create_checkbox(self, layout, label_text):
        """Create a QCheckBox for boolean options."""
        checkbox = QCheckBox(label_text)
        checkbox.setChecked(self.checkbox_states.get(label_text, False))
        layout.addWidget(checkbox)
        return checkbox

    def browse_output_directory(self):
        """Open a file dialog to select an output directory."""
        directory = QFileDialog.getExistingDirectory(
            self, "Select Output Directory")
        if directory:
            self.output_directory_input.setText(directory)

    def browse_config_file(self):
        """Open a file dialog to select a configuration file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Configuration File")
        if file_path:
            self.config_file_input.setText(file_path)

    def get_checkbox_states(self):
        """Return the states of the checkboxes, combo boxes, and inputs.

        Returns:
            dict: A dictionary containing the current states of the dialog's
                  settings inputs.
        """
        return {
            "Set Output Directory": self.output_directory_input.text(),
            "Set OSC Port": self.set_osc_ip_input.text(),
            "Set OSC Port": self.set_osc_port_input.text(),
            "Send OSC": self.send_osc_checkbox.isChecked(),
            # "Set Always on Top": self.always_on_top_checkbox.isChecked(),
            # "Set History Selector": self.history_selector_input.text(),
            # "Set Sensitivity": self.sensitivity_input.text(),
            # "Set Configuration File": self.config_file_input.text(),
            # "Set Audio Input": self.audio_input_selector.currentText(),
            # "Set Audio Output": self.audio_output_selector.currentText(),
            "Set User": self.user_input.text(),
            # "Set Hotkey": self.hotkey.text(),
            # "Enable Filestamps": self.filestamps_checkbox.isChecked(),
            # "Enable Post-Performance Analytics": self.analytics_checkbox.isChecked(),
            # "Set History Navigation": self.history_navigation_input.text(),
        }
