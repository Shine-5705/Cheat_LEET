#!/bin/bash
# LeetCode Automation Quick Start Guide

set -e  # Exit on any error

echo "🚀 LeetCode Automation Quick Start"
echo "=================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "❌ Python is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Use python3 if available, otherwise python
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

echo "✅ Python found: $($PYTHON_CMD --version)"

# Install dependencies
echo "📦 Installing dependencies..."
$PYTHON_CMD -m pip install -r requirements.txt

# Install Playwright browsers
echo "🌐 Installing Playwright browsers..."
$PYTHON_CMD -m playwright install chromium

# Check setup
echo "🔍 Checking setup..."
$PYTHON_CMD setup_check.py

echo ""
echo "🎯 Next steps:"
echo "1. Edit .env file with your OpenAI API key"
echo "2. Run: $PYTHON_CMD storage_state_login.py (for authentication)"
echo "3. Run: $PYTHON_CMD ultimate_leetcode_automation.py (to start automation)"
echo ""
echo "🔧 Alternative if browser automation fails:"
echo "   Run: $PYTHON_CMD manual_login_helper.py"
echo ""
echo "📖 For detailed instructions, see README.md"
echo ""
echo "✅ Setup complete! Happy coding! 🎯"