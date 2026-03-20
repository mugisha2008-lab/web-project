@echo off
echo ========================================
echo    PYTHON PATH FIX TOOL
echo ========================================
echo.
echo This script will disable Windows Store Python alias
echo and allow proper Python usage.
echo.
echo Choose an option:
echo 1. Disable Python alias (RECOMMENDED)
echo 2. Test Python installation
echo 3. Exit
echo.
set /p choice=Your choice: 

if "%choice%"=="1" (
    echo Disabling Python alias...
    reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\App Execution Aliases\python.exe" /f
    echo Python alias disabled successfully!
    echo.
    echo Please restart your terminal/command prompt and try:
    echo   python -m pip install -r requirements.txt
    echo   python app.py
    echo.
)
if "%choice%"=="2" (
    echo Testing Python installation...
    python --version 2>nul
    if %errorlevel% equ 0 (
        echo Python is working!
        echo Testing pip...
        python -m pip --version 2>nul
        if %errorlevel% equ 0 (
            echo pip is working!
            echo Ready to install dependencies.
        ) else (
            echo pip is not working. Try disabling alias first.
        )
    ) else (
        echo Python is not found in PATH.
        echo Try option 1 to disable alias.
    )
)
if "%choice%"=="3" (
    echo Exiting...
)
echo.
pause
