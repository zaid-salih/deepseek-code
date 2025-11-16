@echo off
REM deepseek-code/setup.bat
echo 🚀 DeepSeek-Code Setup for Windows
echo ================================

echo Step 1: Initializing configuration...
python initialize_config.py

if %errorlevel% neq 0 (
    echo ❌ Initialization failed
    pause
    exit /b 1
)

echo Step 2: Running setup wizard...
python quick_setup.py

if %errorlevel% neq 0 (
    echo ❌ Setup failed
    pause
    exit /b 1
)

echo.
echo ✅ Setup completed successfully!
echo.
echo You can now use:
echo   deepseek-code chat
echo   deepseek-code analyze ^<file^>
echo   deepseek-code team workflow-status
echo.
pause