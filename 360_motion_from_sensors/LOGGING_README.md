# Console Error Logging System

This system captures all JavaScript console logs, errors, and warnings from motion_viewer.html and displays them in real-time in your terminal.

## Setup

1. **Start the log server** (in one terminal):
   ```bash
   cd /home/migero/projects/gopro360-converter/360_motion_from_sensors
   python3 log_server.py
   ```

2. **Start the HTTP server** (in another terminal):
   ```bash
   cd /home/migero/projects/gopro360-converter/360_motion_from_sensors
   python3 -m http.server 8000
   ```

3. **Open the page** in your browser:
   ```
   http://localhost:8000/motion_viewer.html
   ```

## How It Works

- The HTML file has console logging code at the very top (before anything else loads)
- It hooks into `console.log()`, `console.error()`, and `console.warn()`
- It captures uncaught errors and unhandled promise rejections
- All logs are sent to `http://localhost:8001/log` via POST requests
- The `log_server.py` receives and displays them with color coding:
  - 🔴 RED = Errors
  - 🟡 YELLOW = Warnings  
  - 🟢 GREEN = Logs

## Usage

Just keep the log server running while you work on the HTML file. Every time you save changes and refresh the browser, you'll see any console output in the log server terminal.

## Stopping

Press `Ctrl+C` in the log server terminal to stop it.

## Files

- `log_server.py` - Python HTTP server that receives and displays logs
- `motion_viewer.html` - Has console capture code at the top (lines 7-75)
- `visualize_motion_stream.py` - Generates HTML with logging code included
