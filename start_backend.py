#!/usr/bin/env python3
"""
Startup script for the 2D to 3D Image Converter Backend
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    # Change to the backend directory
    backend_dir = Path(__file__).parent / "backend"
    os.chdir(backend_dir)
    
    print("Starting 2D to 3D Image Converter Backend...")
    print("=" * 50)
    
    # Check if virtual environment is activated
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("Warning: Virtual environment not detected. Please activate your virtual environment first.")
        print("Run: source venv/Scripts/activate (Windows) or source venv/bin/activate (Linux/Mac)")
        return
    
    # Check if requirements are installed
    try:
        import fastapi
        import torch
        import cv2
        import trimesh
        print("✓ All required packages are installed")
    except ImportError as e:
        print(f"✗ Missing required package: {e}")
        print("Please install requirements: pip install -r requirements.txt")
        return
    
    # Start the server
    try:
        print("Starting FastAPI server...")
        print("API will be available at: http://localhost:8000")
        print("API documentation at: http://localhost:8000/docs")
        print("Press Ctrl+C to stop the server")
        print("=" * 50)
        
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ])
        
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Error starting server: {e}")

if __name__ == "__main__":
    main() 