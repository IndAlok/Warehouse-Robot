@echo off
echo ================================================
echo Warehouse Robot - Complete Setup Script
echo ================================================
echo.

echo Step 1: Installing PostgreSQL (if not installed)
echo Please ensure PostgreSQL is installed on your system
echo Download from: https://www.postgresql.org/download/windows/
echo.
pause

echo.
echo Step 2: Creating Python Virtual Environment...
python -m venv venv
call venv\Scripts\activate.bat

echo.
echo Step 3: Installing Python dependencies...
pip install --upgrade pip
pip install -r requirements.txt

echo.
echo Step 4: Setting up PostgreSQL database...
echo Please create the database manually:
echo   1. Open pgAdmin or psql
echo   2. Create database: CREATE DATABASE warehouse_db;
echo   3. Update credentials in .env file if needed
echo.
pause

echo.
echo Step 5: Initializing database tables and seed data...
python setup_database.py

echo.
echo ================================================
echo Setup Complete!
echo ================================================
echo.
echo To start the server: run.bat
echo To start the robot scanner: start_robot.bat
echo.
echo Server will be available at: http://localhost:5000
echo Video stream at: http://localhost:5000/video_feed
echo.
pause
