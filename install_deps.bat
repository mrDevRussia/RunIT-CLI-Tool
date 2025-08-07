@echo off
setlocal

REM RunIT CLI Tool Dependencies Installer
REM Automatically installs all required dependencies for RunIT

echo ===============================================
echo RunIT CLI Tool - Dependencies Installer
echo ===============================================
echo.

REM Check if Python is installed and get version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
if "%PYTHON_VERSION%"=="" (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.8 or higher from https://www.python.org/downloads/
    echo and make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

echo [INFO] Detected Python %PYTHON_VERSION%

REM Check Python version compatibility
for /f "tokens=1,2 delims=." %%a in ("%PYTHON_VERSION%") do (
    set PYTHON_MAJOR=%%a
    set PYTHON_MINOR=%%b
)

if %PYTHON_MAJOR% LSS 3 (
    echo [ERROR] Python 3.8 or higher is required. You have Python %PYTHON_VERSION%.
    echo Please install a newer version from https://www.python.org/downloads/
    pause
    exit /b 1
) else if %PYTHON_MAJOR% EQU 3 if %PYTHON_MINOR% LSS 8 (
    echo [WARNING] Python 3.8 or higher is recommended. You have Python %PYTHON_VERSION%.
    echo Some features may not work correctly.
    echo.
    echo Press any key to continue anyway or Ctrl+C to cancel...
    pause >nul
)

echo [INFO] Python is installed. Proceeding with dependency installation...
echo.

REM Check if pip is available
pip --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] pip is not available. Trying to install it...
    python -m ensurepip --upgrade
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Failed to install pip. Please install it manually.
        pause
        exit /b 1
    )
)

echo [INFO] Installing Python dependencies...
echo.

REM Install Python dependencies from deps/dependencies.txt
echo [INFO] Installing dependencies from deps/dependencies.txt...
pip install -r deps/dependencies.txt
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to install Python dependencies.
    pause
    exit /b 1
)

echo [INFO] Python dependencies installed successfully.
echo [INFO] Verifying installations...

REM Verify key dependencies
python -c "import requests, colorama, tqdm, pathlib, typing, json" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Some core dependencies may not have installed correctly.
    echo Please run this script again if you encounter any issues when running RunIT.
) else (
    echo [INFO] Core dependencies verified successfully.
)
echo.

REM Check if Node.js is installed (for localtunnel and other JS features)
node --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Node.js is not installed or not in PATH.
    echo Some features like localtunnel for sharing may not work.
    echo If you need these features, please install Node.js from https://nodejs.org/
    echo.
) else (
    echo [INFO] Node.js is installed. Installing Node.js dependencies...
    echo.
    
    REM Check if npm is available
    npm --version >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        echo [WARNING] npm is not available. Skipping Node.js dependencies.
    ) else (
        REM Install Node.js dependencies from package.json if it exists
        if exist package.json (
            npm install
            if %ERRORLEVEL% NEQ 0 (
                echo [WARNING] Failed to install Node.js dependencies from package.json.
                echo Some features may not work properly.
            ) else (
                echo [INFO] Node.js dependencies installed successfully.
            )
        )
        
        REM Install localtunnel globally
        echo [INFO] Installing localtunnel globally...
        npm install -g localtunnel
        if %ERRORLEVEL% NEQ 0 (
            echo [WARNING] Failed to install localtunnel globally.
            echo Sharing functionality may not work properly.
        ) else (
            echo [INFO] localtunnel installed successfully.
        )
    )
    echo.
)

echo ===============================================
echo All dependencies installed successfully!
echo RunIT is ready to use.
echo.
echo [INFO] Optional dependencies information:
echo - fastapi, uvicorn: Required for API server functionality
echo - beautifulsoup4, lxml: Required for web scraping features
echo - pillow: Required for image processing features
echo - rich: Required for enhanced terminal output
echo - cryptography: Required for secure operations
echo.
echo [INFO] Note about localtunnel:
echo The localtunnel-client package is not available via pip.
echo For sharing functionality, please install localtunnel via npm:
echo   npm install -g localtunnel
echo Or use ngrok as an alternative: https://ngrok.com/
echo.
echo Run RunIT.bat to start the tool.
echo ===============================================

pause