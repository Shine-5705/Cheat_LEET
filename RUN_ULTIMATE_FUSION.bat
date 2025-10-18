@echo off
REM Ultimate Enhanced LeetCode Automation - Perfect Fusion
echo.
echo 🚀 ULTIMATE ENHANCED LEETCODE AUTOMATION - PERFECT FUSION
echo =========================================================================
echo 🔄 Auto-refresh authentication from working login system
echo 🧠 Advanced retry logic from ultimate_leetcode_automation.py  
echo 📚 Solutions tab extraction for wrong answers
echo 🎯 Complete scenario coverage and fallback strategies
echo 🤖 OpenAI-powered solution generation with error handling
echo 📱 Anti-detection browser profile
echo =========================================================================
echo.

REM Check if auth state exists
if not exist "automating the login\auth_state.json" (
    echo ❌ No authentication state found!
    echo 🔄 Running initial authentication setup...
    cd "automating the login"
    python save-login.py
    if errorlevel 1 (
        echo ❌ Authentication setup failed!
        pause
        exit /b 1
    )
    cd ..
    echo ✅ Initial authentication completed!
    echo.
)

REM Run the ultimate fusion automation
echo 🚀 Starting ultimate enhanced automation fusion...
python ultimate_enhanced_automation_fusion.py

REM Check results
if errorlevel 1 (
    echo.
    echo ⚠️ Automation completed with some issues.
    echo 🔄 This may be normal for complex problems requiring manual review.
    echo 💡 Check the console output above for detailed status.
    echo.
) else (
    echo.
    echo ✅ Ultimate automation completed successfully!
    echo.
)

echo.
echo 🎯 Ultimate enhanced automation fusion completed!
echo =========================================================================
pause