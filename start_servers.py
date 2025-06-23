#!/usr/bin/env python3
import subprocess
import sys
import time
import os
from pathlib import Path

def start_fastapi():
    """Start the FastAPI server"""
    print("Starting FastAPI server...")
    return subprocess.Popen([
        sys.executable, "server/main.py"
    ], cwd=".")

def start_vite():
    """Start the Vite dev server"""
    print("Starting Vite dev server...")
    return subprocess.Popen([
        "npx", "vite", "--host", "0.0.0.0", "--port", "3000"
    ], cwd="client")

def main():
    # Start both servers
    fastapi_process = start_fastapi()
    time.sleep(2)  # Give FastAPI time to start
    
    vite_process = start_vite()
    
    print("Both servers started. FastAPI on port 5000, Vite on port 3000")
    print("Press Ctrl+C to stop both servers")
    
    try:
        # Wait for processes
        fastapi_process.wait()
        vite_process.wait()
    except KeyboardInterrupt:
        print("\nStopping servers...")
        fastapi_process.terminate()
        vite_process.terminate()
        fastapi_process.wait()
        vite_process.wait()
        print("Servers stopped.")

if __name__ == "__main__":
    main()