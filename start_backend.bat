@echo off
echo Starting 2D to 3D Image Converter Backend...
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo Virtual environment not found. Creating one...
    python -m venv venv
    if errorlevel 1 (
        echo Failed to create virtual environment. Please install Python 3.8+ first.
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if requirements are installed
echo Checking dependencies...
python -c "import fastapi, torch, cv2, trimesh" 2>nul
if errorlevel 1 (
    echo Installing requirements...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo Failed to install requirements. Please check your internet connection.
        pause
        exit /b 1
    )
)

echo.
echo Starting FastAPI server...
echo API will be available at: http://localhost:8000
echo API documentation at: http://localhost:8000/docs
echo Press Ctrl+C to stop the server
echo.

REM Start the server
cd backend
python run.py

pause 