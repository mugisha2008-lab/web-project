@echo off
echo Starting Mugisha Learning Platform...
echo.

echo [1/3] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python not found in PATH!
    echo Please install Python from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

echo Python found successfully!

echo.
echo [2/3] Installing Python dependencies...
pip install -r requirements.txt

echo.
echo [3/3] Starting backend server...
echo Backend will run on: http://localhost:5000
echo Frontend should be running on: http://localhost:3000
echo.
python app.py

pause
