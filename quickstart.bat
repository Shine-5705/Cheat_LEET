@echo off
REM LeetCode Automation Quick Start Guide for Windows

echo 🚀 LeetCode Automation Quick Start
echo ==================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.8+ first.
    pause
    exit /b 1
)

echo ✅ Python found
python --version

REM Install dependencies
echo 📦 Installing dependencies...
pip install -r requirements.txt

REM Install Playwright browsers
echo 🌐 Installing Playwright browsers...
python -m playwright install chromium

REM Check setup
echo 🔍 Checking setup...
python setup_check.py

echo.
echo 🎯 Next steps:
echo 1. Edit .env file with your OpenAI API key
echo 2. Run: python storage_state_login.py (for authentication)
echo 3. Run: python ultimate_leetcode_automation.py (to start automation)
echo.
echo 🔧 Alternative if browser automation fails:
echo    Run: python manual_login_helper.py
echo.
echo 📖 For detailed instructions, see README.md
echo.
pause