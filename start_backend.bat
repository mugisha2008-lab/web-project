@echo off
echo Starting Mugisha Learning Platform Backend...
echo.

REM Set Python path
set PYTHON_PATH=C:\Users\SOD\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra1\python.exe

if exist "%PYTHON_PATH%" (
    echo Found Python at: %PYTHON_PATH%
    echo.
    echo Installing dependencies...
    "%PYTHON_PATH%" -m pip install -r requirements.txt
    
    if !errorlevel! equ 0 (
        echo Dependencies installed successfully!
        echo.
        echo Starting backend server...
        echo Backend will run on: http://localhost:5000
        echo Press Ctrl+C to stop the server
        echo.
        "%PYTHON_PATH%" app.py
    ) else (
        echo Failed to install dependencies.
    )
) else (
    echo Python not found at expected location.
    echo Searching for Python...
    
    REM Try alternative paths
    for %%p in (
        "C:\Users\SOD\AppData\Local\Microsoft\WindowsApps\python.exe"
        "C:\Program Files\Python311\python.exe"
        "C:\Program Files\Python\python.exe"
    ) do (
        if exist "%%p" (
            echo Found Python at: %%p
            set PYTHON_PATH=%%p
            goto :found
        )
    )
    
    :found
    if defined PYTHON_PATH (
        echo Installing dependencies with: %PYTHON_PATH%
        "%PYTHON_PATH%" -m pip install -r requirements.txt
        
        if !errorlevel! equ 0 (
            echo Dependencies installed successfully!
            echo.
            echo Starting backend server...
            echo Backend will run on: http://localhost:5000
            echo Press Ctrl+C to stop the server
            echo.
            "%PYTHON_PATH%" app.py
        ) else (
            echo Failed to install dependencies.
        )
    ) else (
        echo Python not found in any standard location.
        echo Please install Python from: https://www.python.org/downloads/
        echo Make sure to check "Add Python to PATH" during installation.
    )
)

echo.
pause
