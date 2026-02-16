#!/usr/bin/env python3
"""
Watch motion_viewer.html for changes and display browser console errors.
Usage: python3 watch_console.py
Press Ctrl+C to stop.
"""

import time
import os
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.common.exceptions import WebDriverException

HTML_FILE = "motion_viewer.html"
URL = "http://localhost:8000/motion_viewer.html"

def get_file_mtime():
    """Get the last modification time of the HTML file."""
    return os.path.getmtime(HTML_FILE) if os.path.exists(HTML_FILE) else 0

def setup_driver():
    """Setup Firefox driver with console logging enabled."""
    options = Options()
    options.add_argument('--headless')
    
    # Enable browser console logging
    options.set_preference('devtools.console.stdout.content', True)
    
    try:
        driver = webdriver.Firefox(options=options)
        return driver
    except Exception as e:
        print(f"Error setting up Firefox driver: {e}")
        print("Make sure you have geckodriver installed: sudo apt install firefox-geckodriver")
        return None

def get_console_logs(driver):
    """Extract console logs from the browser."""
    logs = []
    try:
        # Get browser logs
        browser_logs = driver.get_log('browser')
        for entry in browser_logs:
            level = entry.get('level', 'INFO')
            message = entry.get('message', '')
            timestamp = entry.get('timestamp', 0)
            logs.append(f"[{level}] {message}")
    except Exception as e:
        # Fallback: try to execute JavaScript to get console logs
        try:
            js_logs = driver.execute_script("""
                var logs = [];
                var oldLog = console.log;
                var oldError = console.error;
                var oldWarn = console.warn;
                
                console.log = function() {
                    logs.push(['LOG', Array.from(arguments).join(' ')]);
                    oldLog.apply(console, arguments);
                };
                console.error = function() {
                    logs.push(['ERROR', Array.from(arguments).join(' ')]);
                    oldError.apply(console, arguments);
                };
                console.warn = function() {
                    logs.push(['WARN', Array.from(arguments).join(' ')]);
                    oldWarn.apply(console, arguments);
                };
                
                return window.capturedLogs || [];
            """)
            for log_entry in js_logs:
                logs.append(f"[{log_entry[0]}] {log_entry[1]}")
        except:
            pass
    
    return logs

def inject_console_capture(driver):
    """Inject JavaScript to capture console logs."""
    try:
        driver.execute_script("""
            if (!window.consoleHooked) {
                window.consoleHooked = true;
                window.capturedLogs = [];
                
                var oldLog = console.log;
                var oldError = console.error;
                var oldWarn = console.warn;
                
                console.log = function() {
                    var msg = Array.from(arguments).map(a => String(a)).join(' ');
                    window.capturedLogs.push(['LOG', msg]);
                    oldLog.apply(console, arguments);
                };
                
                console.error = function() {
                    var msg = Array.from(arguments).map(a => String(a)).join(' ');
                    window.capturedLogs.push(['ERROR', msg]);
                    oldError.apply(console, arguments);
                };
                
                console.warn = function() {
                    var msg = Array.from(arguments).map(a => String(a)).join(' ');
                    window.capturedLogs.push(['WARN', msg]);
                    oldWarn.apply(console, arguments);
                };
                
                // Capture uncaught errors
                window.addEventListener('error', function(e) {
                    var msg = 'Uncaught ' + e.error + ' at ' + e.filename + ':' + e.lineno + ':' + e.colno;
                    window.capturedLogs.push(['ERROR', msg]);
                    console.error(msg);
                });
                
                // Capture unhandled promise rejections
                window.addEventListener('unhandledrejection', function(e) {
                    var msg = 'Unhandled promise rejection: ' + e.reason;
                    window.capturedLogs.push(['ERROR', msg]);
                    console.error(msg);
                });
            }
        """)
        return True
    except Exception as e:
        print(f"Failed to inject console capture: {e}")
        return False

def check_page_errors(driver):
    """Check for JavaScript errors on the page."""
    try:
        # Wait a bit for page to load and execute
        time.sleep(3)
        
        # Get captured console logs
        try:
            captured_logs = driver.execute_script("return window.capturedLogs || [];")
        except Exception as e:
            print(f"Failed to get logs: {e}")
            captured_logs = []
        
        if captured_logs:
            print("\n" + "="*60)
            print("CONSOLE OUTPUT:")
            print("="*60)
            for log_entry in captured_logs:
                try:
                    level, message = log_entry
                    color = ""
                    reset = "\033[0m"
                    
                    if level == "ERROR":
                        color = "\033[91m"  # Red
                    elif level == "WARN":
                        color = "\033[93m"  # Yellow
                    else:
                        color = "\033[92m"  # Green
                    
                    print(f"{color}[{level}]{reset} {message}")
                except Exception as e:
                    print(f"Error displaying log: {log_entry} - {e}")
            print("="*60)
            
            # Clear the logs after displaying
            try:
                driver.execute_script("window.capturedLogs = [];")
            except:
                pass
            return True
        return False
        
    except Exception as e:
        print(f"Error checking page: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("Starting console watcher...")
    print(f"Watching: {HTML_FILE}")
    print(f"URL: {URL}")
    print("Press Ctrl+C to stop\n")
    
    driver = setup_driver()
    if not driver:
        return
    
    last_mtime = 0
    
    try:
        while True:
            current_mtime = get_file_mtime()
            
            if current_mtime != last_mtime:
                if last_mtime > 0:
                    print(f"\n📝 File changed, reloading... (at {time.strftime('%H:%M:%S')})")
                else:
                    print(f"🌐 Loading page for the first time...")
                
                try:
                    driver.get(URL)
                    
                    # Wait for page to start loading
                    time.sleep(1)
                    
                    # Try to get browser logs first (Firefox specific)
                    try:
                        browser_logs = driver.get_log('browser')
                        if browser_logs:
                            print("\n" + "="*60)
                            print("BROWSER LOGS (from Firefox):")
                            print("="*60)
                            for entry in browser_logs:
                                level = entry.get('level', 'INFO')
                                message = entry.get('message', '')
                                print(f"[{level}] {message}")
                            print("="*60)
                    except Exception as e:
                        # Firefox doesn't always support get_log
                        pass
                    
                    # Now inject and check our custom capture
                    inject_console_capture(driver)
                    
                    # Check for errors after a short delay
                    has_output = check_page_errors(driver)
                    
                    if not has_output:
                        print("✅ No console errors or warnings detected")
                    
                except WebDriverException as e:
                    print(f"❌ Error loading page: {e}")
                    print("   Make sure the HTTP server is running: python3 -m http.server 8000")
                
                last_mtime = current_mtime
            
            time.sleep(0.5)  # Check every 500ms
            
    except KeyboardInterrupt:
        print("\n\nStopping watcher...")
    finally:
        driver.quit()
        print("Driver closed. Goodbye!")

if __name__ == "__main__":
    main()
