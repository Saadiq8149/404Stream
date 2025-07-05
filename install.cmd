@echo off
cmd /k
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python is not installed on this system.
    echo Please install Python before running this script.
    pause
)

python install.py
pause
