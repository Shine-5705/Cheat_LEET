@echo off
echo Installing Playwright for Python...
pip install playwright
echo.
echo Installing Playwright browsers...
python -m playwright install chromium
echo.
echo ✅ Playwright setup completed!
echo.
echo Now you can run:
echo   npm run save-login    - To save your Google login session
echo   npm run playwright-auto - To automatically login to LeetCode
pause