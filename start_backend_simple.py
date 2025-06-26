#!/usr/bin/env python3
"""
Simplified startup script for the 2D to 3D Image Converter Backend
Uses basic requirements without MiDaS for easier setup
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    # Change to the backend directory
    backend_dir = Path(__file__).parent / "backend"
    os.chdir(backend_dir)
    
    print("Starting 2D to 3D Image Converter Backend (Simplified)...")
    print("=" * 60)
    
    # Check if virtual environment is activated
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("Warning: Virtual environment not detected. Please activate your virtual environment first.")
        print("Run: source venv/Scripts/activate (Windows) or source venv/bin/activate (Linux/Mac)")
        return
    
    # Check if basic requirements are installed
    try:
        import fastapi
        import torch
        import cv2
        import trimesh
        print("✓ All required packages are installed")
    except ImportError as e:
        print(f"✗ Missing required package: {e}")
        print("Installing simplified requirements...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "../requirements_simple.txt"], check=True)
            print("✓ Requirements installed successfully")
        except subprocess.CalledProcessError:
            print("✗ Failed to install requirements. Please check your internet connection.")
            return
    
    # Start the server
    try:
        print("Starting FastAPI server...")
        print("API will be available at: http://localhost:8000")
        print("API documentation at: http://localhost:8000/docs")
        print("Note: Using simple depth estimation (no MiDaS)")
        print("Press Ctrl+C to stop the server")
        print("=" * 60)
        
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