#!/usr/bin/env python3
"""
Run script for the 2D to 3D Image Converter Backend
"""

import uvicorn
from main import app

if __name__ == "__main__":
    print("Starting 2D to 3D Image Converter Backend...")
    print("API will be available at: http://localhost:8000")
    print("API documentation at: http://localhost:8000/docs")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 