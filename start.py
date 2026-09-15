#!/usr/bin/env python3
"""
AI Prescription Analyzer - Quick Start Script
Run this script to start both backend and frontend services.
"""

import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path

def print_banner():
    """Print startup banner."""
    banner = """
    ╔══════════════════════════════════════════════════════════════════════════════╗
    ║                       🏥 AI Prescription Analyzer                            ║
    ║                     Healthcare Guardian Platform                             ║
    ║                                                                              ║
    ║  • OCR & NLP Prescription Processing                                         ║
    ║  • Drug Interaction Detection                                                ║
    ║  • AI Health Assistant                                                       ║
    ║  • Pharmacy Finder                                                           ║
    ║  • HIPAA/GDPR Compliant                                                      ║
    ╚══════════════════════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        sys.exit(1)
    print(f"✅ Python {sys.version.split()[0]} detected")

def check_dependencies():
    """Check if required dependencies are installed."""
    required_packages = ['fastapi', 'streamlit', 'uvicorn']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} is installed")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} is missing")
    
    if missing_packages:
        print(f"\n📦 Installing missing packages: {', '.join(missing_packages)}")
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing_packages)
        print("✅ All dependencies installed")

def setup_environment():
    """Setup environment variables."""
    env_file = Path(".env")
    env_template = Path(".env.template")
    
    if not env_file.exists() and env_template.exists():
        print("📄 Creating .env file from template...")
        env_file.write_text(env_template.read_text())
        print("✅ Environment file created")
        print("⚠️  Please edit .env file with your API keys and configuration")
    elif env_file.exists():
        print("✅ Environment file found")
    else:
        print("⚠️  No environment configuration found")

def start_backend():
    """Start the FastAPI backend."""
    print("\n🚀 Starting Backend API...")
    backend_dir = Path("backend")
    
    if backend_dir.exists():
        os.chdir(backend_dir)
        # Start backend in background
        process = subprocess.Popen([
            sys.executable, "main.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        os.chdir("..")
        
        # Wait a moment for backend to start
        time.sleep(3)
        print("✅ Backend API started at http://localhost:8000")
        return process
    else:
        print("❌ Backend directory not found")
        return None

def start_frontend():
    """Start the Streamlit frontend."""
    print("\n🖥️  Starting Frontend Application...")
    frontend_dir = Path("frontend/streamlit_app")
    
    if frontend_dir.exists():
        # Start Streamlit
        process = subprocess.Popen([
            sys.executable, "-m", "streamlit", "run", 
            str(frontend_dir / "main.py"),
            "--server.port", "8501"
        ])
        
        # Wait a moment for frontend to start
        time.sleep(5)
        print("✅ Frontend started at http://localhost:8501")
        
        # Open browser
        try:
            webbrowser.open("http://localhost:8501")
            print("🌐 Opening browser...")
        except Exception as e:
            print(f"⚠️  Could not open browser automatically: {e}")
        
        return process
    else:
        print("❌ Frontend directory not found")
        return None

def print_usage_info():
    """Print usage information."""
    info = """
    🎉 AI Prescription Analyzer is now running!
    
    📊 Services:
    • Backend API: http://localhost:8000
    • API Documentation: http://localhost:8000/api/docs
    • Frontend App: http://localhost:8501
    
    🔧 Quick Actions:
    1. Register a new account or login
    2. Upload a prescription image for OCR processing
    3. Check drug interactions
    4. Chat with the AI health assistant
    5. Find nearby pharmacies
    
    ⚠️  Important Notes:
    • Make sure to configure your .env file with API keys
    • This is for demonstration purposes - consult healthcare providers for medical advice
    • Press Ctrl+C to stop all services
    
    📖 For detailed documentation, see README.md
    """
    print(info)

def main():
    """Main startup function."""
    try:
        print_banner()
        
        # Pre-flight checks
        check_python_version()
        setup_environment()
        check_dependencies()
        
        # Start services
        backend_process = start_backend()
        frontend_process = start_frontend()
        
        if backend_process and frontend_process:
            print_usage_info()
            
            # Keep processes running
            try:
                frontend_process.wait()
            except KeyboardInterrupt:
                print("\n🛑 Shutting down services...")
                if backend_process:
                    backend_process.terminate()
                if frontend_process:
                    frontend_process.terminate()
                print("✅ Services stopped")
        else:
            print("❌ Failed to start one or more services")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n🛑 Startup cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Startup error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()