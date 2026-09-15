#!/usr/bin/env python3
"""
Simple backend startup script for AI Prescription Analyzer
"""
import os
import sys
import subprocess
from pathlib import Path

def main():
    """Start the FastAPI backend."""
    print("🚀 Starting AI Prescription Analyzer Backend...")
    
    # Change to backend directory
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("❌ Backend directory not found")
        return
    
    # Set environment variable for debug mode
    os.environ['DEBUG'] = 'True'
    
    try:
        # Start the backend using uvicorn directly
        os.chdir(backend_dir)
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "main:app",
            "--host", "127.0.0.1",
            "--port", "8000",
            "--reload",
            "--log-level", "info"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Backend server stopped")
    except Exception as e:
        print(f"❌ Error starting backend: {e}")
        print("💡 Make sure you have FastAPI and uvicorn installed:")
        print("   pip install fastapi uvicorn")

if __name__ == "__main__":
    main()