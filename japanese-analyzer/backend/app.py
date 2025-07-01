#!/usr/bin/env python3
"""
Unified Python Services Launcher for Japanese Text Analyzer
Starts both the Parser Service (port 8001) and OCR Service (port 8000) simultaneously
"""

import subprocess
import threading
import time
import sys
import os
import signal
from pathlib import Path

class ServiceManager:
    def __init__(self):
        self.processes = []
        self.backend_dir = Path(__file__).parent
        
    def get_python_executable(self, service_dir):
        """Get the correct Python executable for each service"""
        # Check for Windows venv first
        windows_python = service_dir / ".venv" / "Scripts" / "python.exe"
        if windows_python.exists():
            return str(windows_python)
        
        # Check for Linux venv
        linux_python = service_dir / ".venv" / "bin" / "python"
        if linux_python.exists():
            return str(linux_python)
        
        # Check parent directory venv (shared)
        parent_venv_win = self.backend_dir / "venv" / "Scripts" / "python.exe"
        if parent_venv_win.exists():
            return str(parent_venv_win)
        
        parent_venv_linux = self.backend_dir / "venv" / "bin" / "python"
        if parent_venv_linux.exists():
            return str(parent_venv_linux)
        
        # Fallback to system Python
        return "python3" if sys.platform != "win32" else "python"
    
    def start_service(self, service_name, port, service_dir, app_module):
        """Start a single service in a separate thread"""
        def run_service():
            try:
                python_exe = self.get_python_executable(service_dir)
                cmd = [
                    python_exe, "-m", "uvicorn", 
                    f"{app_module}:app", 
                    "--host", "0.0.0.0", 
                    "--port", str(port),
                    "--reload"
                ]
                
                print(f"🚀 Starting {service_name} on port {port}")
                print(f"   Command: {' '.join(cmd)}")
                print(f"   Working directory: {service_dir}")
                
                # Change to service directory
                os.chdir(service_dir)
                
                # Start the process
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True,
                    bufsize=1
                )
                
                self.processes.append(process)
                
                # Stream output with service prefix
                for line in iter(process.stdout.readline, ''):
                    if line.strip():
                        print(f"[{service_name}] {line.strip()}")
                
            except Exception as e:
                print(f"❌ Error starting {service_name}: {e}")
        
        thread = threading.Thread(target=run_service, daemon=True)
        thread.start()
        return thread
    
    def start_all_services(self):
        """Start both OCR and Parser services"""
        print("🎯 Japanese Text Analyzer - Python Services Launcher")
        print("=" * 60)
        
        # Define services
        services = [
            {
                'name': 'OCR Service',
                'port': 8000,
                'dir': self.backend_dir / 'ocr_service',
                'module': 'ocr_server'
            },
            {
                'name': 'Parser Service', 
                'port': 8001,
                'dir': self.backend_dir / 'parser_service',
                'module': 'parser'
            }
        ]
        
        threads = []
        
        # Start each service
        for service in services:
            if not service['dir'].exists():
                print(f"❌ {service['name']} directory not found: {service['dir']}")
                continue
                
            thread = self.start_service(
                service['name'],
                service['port'], 
                service['dir'],
                service['module']
            )
            threads.append(thread)
            time.sleep(2)  # Stagger startup
        
        print("\n✅ All services are starting up...")
        print("\n📍 Service Endpoints:")
        print("   • OCR Service:    http://localhost:8000")
        print("   • Parser Service: http://localhost:8001")
        print("\n🎮 Backend API should connect automatically")
        print("   • Backend API:    http://localhost:3000")
        print("\n⏹️  Press Ctrl+C to stop all services")
        
        try:
            # Keep main thread alive
            while True:
                time.sleep(1)
                # Check if any process has died
                for process in self.processes[:]:  # Copy list to modify during iteration
                    if process.poll() is not None:
                        print(f"⚠️  A service process has stopped (exit code: {process.poll()})")
                        self.processes.remove(process)
                        
        except KeyboardInterrupt:
            self.stop_all_services()
    
    def stop_all_services(self):
        """Stop all running services"""
        print("\n🛑 Stopping all services...")
        
        for process in self.processes:
            try:
                if process.poll() is None:  # Process is still running
                    process.terminate()
                    # Give it a moment to terminate gracefully
                    try:
                        process.wait(timeout=5)
                        print("✅ Service stopped gracefully")
                    except subprocess.TimeoutExpired:
                        print("⚠️  Force killing service...")
                        process.kill()
                        process.wait()
            except Exception as e:
                print(f"❌ Error stopping service: {e}")
        
        print("🏁 All services stopped")

def main():
    """Main entry point"""
    # Handle Ctrl+C gracefully
    def signal_handler(signum, frame):
        print("\n🛑 Received interrupt signal...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Check if we're in the right directory
    if not Path("ocr_service").exists() or not Path("parser_service").exists():
        print("❌ Error: This script must be run from the backend directory")
        print("   Expected structure:")
        print("   backend/")
        print("   ├── app.py (this file)")
        print("   ├── ocr_service/")
        print("   └── parser_service/")
        sys.exit(1)
    
    # Start services
    manager = ServiceManager()
    manager.start_all_services()

if __name__ == "__main__":
    main()