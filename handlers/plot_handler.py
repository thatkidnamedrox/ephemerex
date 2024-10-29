"""
Mouse Movement and Interaction Visualization

This script defines a class `PlotHandler` that processes CSV log files containing
mouse movement, click events, and key presses. The class provides functionality to:
1. Read CSV data, extract relevant information, and export it.
2. Visualize the extracted data in 3D plots, displaying mouse movements, clicks, 
   key presses, and an Actions Per Minute (APM) graph.
3. Utilize PyQt5 for handling GUI interactions, although no GUI components are
   explicitly defined in this snippet.

Dependencies:
- pandas: for data manipulation and analysis.
- matplotlib: for plotting and visualization.
- PyQt5: for GUI functionalities (though not fully implemented in this code).

Usage:
- Instantiate the `PlotHandler` class.
- Call the `handle_csv` method with a window object that contains CSV rows 
  to process the data and generate visualizations.

Class Structure:
- PlotHandler:
    - handle_csv(window): Processes CSV data and triggers graph plotting.
    - plot_graph(data): Plots mouse movements, click events, key presses, and 
      computes APM in a 3D graph.

Note: Ensure that the CSV file contains columns: 'function_name', 'arguments', 
'active_process', and 'time_elapsed' for the code to function properly.
"""

import sys
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import QTimer


class PlotHandler():
    def handle_csv(self, window):
        print(f"Number of entries: {len(window.csv_rows)}")

        # Prepare and export CSV data
        csv_rows = "\n".join(window.csv_rows)
        header = "function_name,arguments,active_process,time_elapsed\n"
        csv_rows = header + csv_rows
        file_path = window.export_data(csv_rows, "log", "csv")

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
