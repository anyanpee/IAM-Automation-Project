@echo off
echo Setting up IAM Automation Project...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Create .env file if it doesn't exist
if not exist .env (
    echo Creating .env file...
    copy .env.example .env
    echo Please edit .env file with your AWS configuration
)

echo.
echo Setup completed successfully!
echo.
echo Next steps:
echo 1. Configure your AWS credentials: aws configure
echo 2. Edit .env file with your settings
echo 3. Run the tool: python src\main.py --help
echo.
pause