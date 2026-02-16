#!/usr/bin/env python3
"""
Simple HTTP server that receives and displays console logs from the browser.
Usage: python3 log_server.py
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import time
from datetime import datetime

class LogHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/log':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                log_data = json.loads(post_data.decode('utf-8'))
                level = log_data.get('level', 'INFO')
                message = log_data.get('message', '')
                timestamp = datetime.now().strftime('%H:%M:%S')
                
                # Color codes
                colors = {
                    'ERROR': '\033[91m',  # Red
                    'WARN': '\033[93m',   # Yellow
                    'LOG': '\033[92m',    # Green
                    'INFO': '\033[94m'    # Blue
                }
                reset = '\033[0m'
                
                color = colors.get(level, '')
                print(f"{timestamp} {color}[{level}]{reset} {message}")
                
            except Exception as e:
                print(f"Error parsing log: {e}")
            
            # Send response
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')
            
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_OPTIONS(self):
        # Handle CORS preflight
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def log_message(self, format, *args):
        # Suppress default request logging
        pass

def main():
    port = 8001
    server = HTTPServer(('localhost', port), LogHandler)
    print(f"🎧 Console log server running on http://localhost:{port}")
    print(f"📝 Waiting for logs from motion_viewer.html...")
    print(f"Press Ctrl+C to stop\n")
    print("="*60)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n" + "="*60)
        print("Stopping log server...")
        server.shutdown()

if __name__ == "__main__":
    main()
