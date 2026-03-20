@echo off
echo Installing Python dependencies...
echo.

REM Try different Python paths
echo Attempting to find Python...
for %%p in (
    "C:\Users\SOD\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra1\python.exe"
    "C:\Users\SOD\AppData\Local\Microsoft\WindowsApps\python.exe"
    "C:\Program Files\Python311\python.exe"
    "C:\Program Files\Python\python.exe"
) do (
    if exist "%%p" (
        echo Found Python at: %%p
        echo Installing dependencies...
        "%%p" -m pip install -r requirements.txt
        if !errorlevel! equ 0 (
            echo Dependencies installed successfully!
            echo.
            echo Starting backend server...
            "%%p" app.py
        ) else (
            echo Failed to install dependencies.
        )
        goto :found
    )
)

echo Python not found in standard locations.
echo Please ensure Python is properly installed.
echo You can download from: https://www.python.org/downloads/
echo.
pause

:found
