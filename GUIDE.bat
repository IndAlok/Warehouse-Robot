@echo off
echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║     Warehouse Robot - Quick Start Guide                 ║
echo ╚══════════════════════════════════════════════════════════╝
echo.
echo 📋 PROJECT STRUCTURE:
echo.
echo Core Files:
echo   • robot.py         - QR scanner with video streaming
echo   • app.py           - Flask server with web dashboard
echo   • database.py      - PostgreSQL database models
echo   • config.py        - Configuration settings
echo.
echo Utility Scripts:
echo   • setup_database.py  - Initialize DB and seed data
echo   • generate_qr.py     - Generate QR codes for products
echo   • test_api.py        - API testing suite
echo   • install.py         - Auto installer
echo.
echo Batch Scripts:
echo   • run.bat          - Start the server
echo   • start_robot.bat  - Start the robot scanner
echo   • setup.bat        - Complete setup wizard
echo.
echo ═══════════════════════════════════════════════════════════
echo.
echo 🚀 QUICK START (3 STEPS):
echo.
echo Step 1: Install Dependencies
echo   python install.py
echo   (or manually: pip install -r requirements.txt)
echo.
echo Step 2: Setup Database
echo   Make sure PostgreSQL is running
echo   python setup_database.py
echo.
echo Step 3: Start the System
echo   Terminal 1: run.bat (starts server)
echo   Terminal 2: start_robot.bat (starts scanner)
echo.
echo ═══════════════════════════════════════════════════════════
echo.
echo 🌐 ACCESS POINTS:
echo.
echo   Dashboard:     http://localhost:5000
echo   Video Stream:  http://localhost:5000/video_feed
echo   API Health:    http://localhost:5000/health
echo   Products API:  http://localhost:5000/products
echo   Scan History:  http://localhost:5000/scan_history
echo.
echo ═══════════════════════════════════════════════════════════
echo.
echo 🧪 TESTING:
echo.
echo   Generate QR codes:  python generate_qr.py
echo   Test API:          python test_api.py
echo   Verify QR:         python test_api.py verify 1/1/1
echo.
echo ═══════════════════════════════════════════════════════════
echo.
echo 📦 QR CODE FORMAT:
echo.
echo   category_id/product_id/location_id
echo.
echo   Examples:
echo     1/1/1  - Dove Soap, Shelf 1 Block A (CORRECT)
echo     2/4/2  - Pantene Shampoo, Shelf 2 Block B (CORRECT)
echo     1/1/2  - Dove Soap at wrong location (MISPLACED)
echo.
echo ═══════════════════════════════════════════════════════════
echo.
echo 🔧 DATABASE INFO:
echo.
echo   Database:  warehouse_db
echo   Tables:    categories, locations, products, scan_logs
echo   Products:  16 products with intelligent dummy data
echo.
echo ═══════════════════════════════════════════════════════════
echo.
echo 📱 FEATURES:
echo.
echo   ✓ Real-time QR code scanning with OpenCV
echo   ✓ Live video streaming to web browser
echo   ✓ Database verification (PostgreSQL)
echo   ✓ Misplacement detection
echo   ✓ Web dashboard with statistics
echo   ✓ Scan history logging
echo   ✓ RESTful API
echo   ✓ Automatic QR code generation
echo.
echo ═══════════════════════════════════════════════════════════
echo.
echo 💡 TIPS:
echo.
echo   • Press 'q' in robot scanner to quit
echo   • Press 'r' to reset current verification
echo   • Update .env file for custom configuration
echo   • Check server terminal for verification logs
echo.
echo ═══════════════════════════════════════════════════════════
echo.
pause
