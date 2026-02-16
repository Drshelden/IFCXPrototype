#!/usr/bin/env python
"""Start script for IFC Processing Server"""

import os
import sys
import subprocess
from pathlib import Path

def check_venv():
    """Check if virtual environment is activated"""
    venv_python = Path('.venv/Scripts/python.exe')
    if venv_python.exists():
        return str(venv_python)
    
    # Try to detect if we're in a venv
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        return sys.executable
    
    return None

def check_dependencies():
    """Check if required packages are installed"""
    required = ['flask', 'werkzeug', 'ifcopenshell']
    missing = []
    
    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    return missing

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    subprocess.check_call([
        sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
    ])
    print("✅ Dependencies installed!")

def start_server():
    """Start the Flask server"""
    print("\n" + "="*50)
    print("🚀 IFC Processing Server")
    print("="*50)
    print("\n📄 Admin Interface: http://localhost:5000")
    print("📁 Data Store: dataStores/fileBased/data/")
    print("🔧 Press Ctrl+C to stop the server\n")
    print("="*50 + "\n")
    
    os.system(f'{sys.executable} app.py')

if __name__ == '__main__':
    # Check for virtual environment
    venv_python = check_venv()
    if venv_python:
        print(f"✅ Using virtual environment: {venv_python}")
    
    # Check dependencies
    missing = check_dependencies()
    if missing:
        print(f"⚠️  Missing packages: {', '.join(missing)}")
        response = input("Install dependencies now? (y/n): ").strip().lower()
        if response == 'y':
            install_dependencies()
        else:
            print("❌ Cannot start server without dependencies")
            sys.exit(1)
    
    # Start server
    try:
        start_server()
    except KeyboardInterrupt:
        print("\n\n✅ Server stopped")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
