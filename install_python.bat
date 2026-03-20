@echo off
echo Installing Python 3.11...
echo.
echo This will download and install Python automatically.
echo Please accept the UAC prompt if it appears.
echo.

REM Download Python installer
echo Downloading Python installer...
powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe' -OutFile 'python-installer.exe'"

if exist python-installer.exe (
    echo.
    echo Starting Python installation...
    echo IMPORTANT: Make sure to check "Add Python to PATH" during installation!
    echo.
    
    REM Run installer silently with PATH addition
    python-installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
    
    echo.
    echo Python installation completed!
    echo Please restart your terminal/command prompt.
    echo.
    
    REM Clean up
    del python-installer.exe
    
) else (
    echo Failed to download Python installer.
    echo Please install manually from: https://www.python.org/downloads/
)

pause
