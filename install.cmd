@echo off
setlocal enabledelayedexpansion

echo.
echo ==========================================
echo         404Stream Installer
echo ==========================================
echo.

REM Check if Python is installed
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed on this system.
    echo.
    echo Please install Python 3.8+ from https://python.org
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

REM Check Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [INFO] Found Python %PYTHON_VERSION%

REM Check if pip is available
python -m pip --version >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] pip is not available.
    echo Please ensure pip is installed with Python.
    echo.
    pause
    exit /b 1
)

echo [INFO] pip is available

REM Check if install.py exists
if not exist "install.py" (
    echo [ERROR] install.py not found in current directory.
    echo Please make sure you're running this from the 404Stream directory.
    echo.
    pause
    exit /b 1
)

echo [INFO] Starting 404Stream installation...
echo.

REM Run the Python installer
python install.py

REM Check if installation was successful
if %errorlevel% equ 0 (
    echo.
    echo ==========================================
    echo     Installation completed successfully!
    echo ==========================================
    echo.
    echo You can now:
    echo 1. Use the desktop shortcut to launch 404Stream
    echo 2. Or run launcher.py from the installation directory
    echo.
) else (
    echo.
    echo ==========================================
    echo        Installation failed!
    echo ==========================================
    echo.
    echo Please check the error messages above.
    echo You may need to run as administrator.
    echo.
)

pause
