@echo off
cls
echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║         WAREHOUSE ROBOT - COMPLETE SYSTEM                ║
echo ╚══════════════════════════════════════════════════════════╝
echo.
echo 📋 Quick Reference:
echo    • Quick Guide: GUIDE.bat
echo    • Management Console: manage.bat  (or python manage.py)
echo    • Quick Reference: python QUICK_REFERENCE.py
echo.
echo ═══════════════════════════════════════════════════════════
echo.
echo 🚀 CHOOSE YOUR ACTION:
echo.
echo   [1] Complete Setup (First Time)
echo   [2] Start Server + Dashboard
echo   [3] Start Robot Scanner
echo   [4] Generate QR Codes
echo   [5] Test API
echo   [6] Management Console (Recommended)
echo   [7] View Quick Reference
echo   [8] Exit
echo.
echo ═══════════════════════════════════════════════════════════
echo.

set /p choice="Enter your choice (1-8): "

if "%choice%"=="1" goto setup
if "%choice%"=="2" goto server
if "%choice%"=="3" goto robot
if "%choice%"=="4" goto qrgen
if "%choice%"=="5" goto test
if "%choice%"=="6" goto manage
if "%choice%"=="7" goto reference
if "%choice%"=="8" goto end

echo Invalid choice. Please run again.
pause
goto end

:setup
cls
echo.
echo ═══════════════════════════════════════════════════════════
echo COMPLETE SETUP - FIRST TIME
echo ═══════════════════════════════════════════════════════════
echo.
echo Step 1: Installing dependencies...
pip install -r requirements.txt
echo.
echo Step 2: Database setup
echo.
echo IMPORTANT: Make sure PostgreSQL is installed and running!
echo Create database: CREATE DATABASE warehouse_db;
echo.
pause
echo.
echo Initializing database...
python setup_database.py
echo.
echo Step 3: Generating QR codes...
python generate_qr.py
echo.
echo ✅ Setup complete!
echo.
echo Next steps:
echo   1. Start server: run.bat
echo   2. Start robot: start_robot.bat
echo   3. Open browser: http://localhost:5000
echo.
pause
goto end

:server
cls
echo.
echo ═══════════════════════════════════════════════════════════
echo STARTING SERVER WITH DASHBOARD
echo ═══════════════════════════════════════════════════════════
echo.
echo 🌐 Dashboard will be available at: http://localhost:5000
echo 📹 Video stream at: http://localhost:5000/video_feed
echo.
echo Press Ctrl+C to stop the server
echo.
pause
python app.py
goto end

:robot
cls
echo.
echo ═══════════════════════════════════════════════════════════
echo STARTING ROBOT SCANNER
echo ═══════════════════════════════════════════════════════════
echo.
echo ⚠️  IMPORTANT: Make sure the server is running first!
echo.
echo Keyboard controls:
echo   • Press 'q' to quit
echo   • Press 'r' to reset verification
echo.
pause
python robot.py
goto end

:qrgen
cls
echo.
echo ═══════════════════════════════════════════════════════════
echo QR CODE GENERATION
echo ═══════════════════════════════════════════════════════════
echo.
echo [1] Generate QR codes for all products
echo [2] Generate test QR codes (with misplaced examples)
echo.
set /p qrchoice="Choose option (1 or 2): "
echo.
if "%qrchoice%"=="1" (
    python generate_qr.py
) else if "%qrchoice%"=="2" (
    python generate_qr.py test
) else (
    echo Invalid choice
)
echo.
pause
goto end

:test
cls
echo.
echo ═══════════════════════════════════════════════════════════
echo API TESTING
echo ═══════════════════════════════════════════════════════════
echo.
echo ⚠️  IMPORTANT: Make sure the server is running first!
echo.
pause
python test_api.py
echo.
pause
goto end

:manage
cls
python manage.py
goto end

:reference
cls
python QUICK_REFERENCE.py
pause
goto end

:end
echo.
echo 👋 Goodbye!
echo.
