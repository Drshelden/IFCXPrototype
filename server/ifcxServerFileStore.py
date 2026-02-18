#!/usr/bin/env python
"""Start script for IFC Processing Server with configurable data store backend"""

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
    required = ['flask', 'werkzeug', 'ifcopenshell', 'flask-cors']
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

def get_data_store_type():
    """Get data store type from environment or user input"""
    # Check environment variable first
    store_type = os.environ.get('IFC_DATA_STORE', '').lower()
    
    if store_type in ['filebased', 'mongodbbased']:
        return store_type
    
    # Ask user
    print("\n📊 Select Data Store Backend:")
    print("   1. fileBased      (File-based storage in dataStores/fileBased/data)")
    print("   2. mongodbBased   (MongoDB storage - currently in development)")
    
    choice = input("\nEnter choice (1 or 2) [1]: ").strip() or "1"
    
    if choice == "1":
        return "fileBased"
    elif choice == "2":
        return "mongodbBased"
    else:
        print("Invalid choice, using fileBased by default")
        return "fileBased"

def start_server(data_store_type='fileBased'):
    """Start the Flask server
    
    Args:
        data_store_type: 'fileBased' or 'mongodbBased'
    """
    print("\n" + "="*50)
    print("🚀 IFC Processing Server")
    print("="*50)
    print(f"\n💾 Data Store Backend: {data_store_type}")
    
    if data_store_type == 'fileBased':
        print("📁 Data Store: dataStores/fileBased/data/")
    elif data_store_type == 'mongodbBased':
        print("🔗 MongoDB Connection: mongodb://localhost:27017")
    
    print("📄 Admin Interface: http://localhost:5000")
    print("🔧 Press Ctrl+C to stop the server\n")
    print("="*50 + "\n")
    
    # Set environment variable for server.py
    env = os.environ.copy()
    env['IFC_DATA_STORE'] = data_store_type
    
    subprocess.call([sys.executable, 'server.py'], env=env)

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
    
    # Get data store type
    data_store_type = get_data_store_type()
    
    # Start server
    try:
        start_server(data_store_type)
    except KeyboardInterrupt:
        print("\n\n✅ Server stopped")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

