# Ephemerex

Download the executable [here](https://drive.google.com/file/d/1Dh8gr5OAZQUw28zqFkXSbdXG2GVy2k_g/view?usp=sharing). Currently available for Windows only.

To build the project yourself, clone the repository, navigate to the project directory, and run:

```bash
pyinstaller --onefile main.py
```

## Overview
Ephemerex is a tool designed to capture and visualize user interactions, such as mouse movements, clicks, and keyboard events. It generates a 3D graphical representation of these interactions, offering insights into user behavior during live coding sessions or performances.

## How It Works

1. **Data Capture**
   - The application utilizes custom modules for event tracking:
     - **MouseHandler**: Logs mouse movements and clicks.
     - **KeyboardHandler**: Captures keyboard inputs and calculates typing speed.
     - **EventHandler**: Integrates mouse and keyboard data, sending it as OSC messages for real-time processing.

2. **Data Visualization**
   - **matplotlib** is used to plot the captured data in 3D, visualizing interaction patterns over time.
   - The application displays actions per minute (APM) to offer performance metrics.

3. **User Interface**
   - Built with **PyQt5**, the GUI allows users to start recording, view visualizations, and configure settings. Users can adjust metrics and view additional details in dedicated dialogs.

## Modules

- **EventHandler**: Manages event tracking for comprehensive logging.
- **KeyboardHandler**: Processes keyboard inputs and supports text analysis.
- **MouseHandler**: Tracks and records mouse activity.
- **ProcessHandler**: Monitors CPU usage for active processes.
- **PlotHandler**: Manages data visualization for logged interactions.

## Applications in Live Coding

1. **Performance Analysis**
   - Visualization of user interactions helps performers analyze workflows and identify ways to optimize inputs for improved efficiency during live performances.

2. **Practice Feedback**
   - Reviewing interaction patterns allows users to refine techniques and improve coding fluency through targeted practice.

3. **Documentation**
   - Recorded interactions provide a reference for development over time, allowing users to track progress and establish performance benchmarks.

## Importance of Ephemerex

- **Enhanced Insight**: Visual representations of user interactions reveal patterns not evident through standard logging, fostering more effective live coding practices.
- **Community Engagement**: Shared visualizations allow coders to connect with audiences, offering deeper insights into the technical processes behind live performances.
- **Learning Support**: For beginners, interaction visualization demystifies coding and encourages experimentation.

Ephemerex serves as a valuable tool for enhancing live coding experiences, promoting continuous improvement, and strengthening connections between performers and audiences.
