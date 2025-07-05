@echo off
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python is not installed on this system.
    echo Please install Python before running this script.
    pause
    exit /b 1
)

python install.py
pause
