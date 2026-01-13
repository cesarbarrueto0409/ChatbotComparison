#!/usr/bin/env python3
"""
Simple HTTP server to serve the frontend files
"""
import http.server
import socketserver
import os
import webbrowser
from pathlib import Path

# Configuration
PORT = 8080
FRONTEND_DIR = "frontend"

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=FRONTEND_DIR, **kwargs)
    
    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

def main():
    # Check if frontend directory exists
    if not os.path.exists(FRONTEND_DIR):
        print(f"Frontend directory '{FRONTEND_DIR}' not found!")
        return
    
    # Change to project root directory
    os.chdir(Path(__file__).parent)
    
    # Create server
    with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
        print(f"Serving frontend at http://localhost:{PORT}")
        print(f"Serving files from: {os.path.abspath(FRONTEND_DIR)}")
        print("Opening browser...")
        
        # Open browser
        webbrowser.open(f"http://localhost:{PORT}")
        
        print("Press Ctrl+C to stop the server")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped")

if __name__ == "__main__":
    main()