"""
╔══════════════════════════════════════════════════════════════════╗
║           WAREHOUSE ROBOT - QUICK REFERENCE CARD                 ║
╚══════════════════════════════════════════════════════════════════╝

INSTALLATION (First Time):
━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. pip install -r requirements.txt
2. Create PostgreSQL database: warehouse_db
3. python setup_database.py
4. python generate_qr.py  (optional - for test QR codes)

DAILY OPERATION:
━━━━━━━━━━━━━━━━
Terminal 1: python app.py         (start server)
Terminal 2: python robot.py        (start scanner)
Browser:    http://localhost:5000  (open dashboard)

OR USE MANAGEMENT CONSOLE:
━━━━━━━━━━━━━━━━━━━━━━━━━━
python manage.py  (interactive menu for all operations)

FILE PURPOSES:
━━━━━━━━━━━━━━
robot.py          - QR scanner with camera
app.py            - Web server + dashboard (USE THIS)
server.py         - Standalone server (without dashboard)
database.py       - PostgreSQL models
config.py         - Settings
seed_data.py      - Database dummy data
setup_database.py - Initialize DB
generate_qr.py    - Create QR code images
test_api.py       - API testing
install.py        - Auto installer
manage.py         - Management console

QR CODE EXAMPLES:
━━━━━━━━━━━━━━━━━
1/1/1  → Dove Soap, Shelf 1 Block A (✓ correct)
2/4/2  → Pantene Shampoo, Shelf 2 Block B (✓ correct)
3/7/3  → Colgate Toothpaste, Shelf 3 Block C (✓ correct)
1/1/2  → Dove Soap at WRONG shelf (✗ misplaced)

API ENDPOINTS:
━━━━━━━━━━━━━━
GET  /                    → Dashboard
GET  /video_feed          → Live video
GET  /products            → All products
GET  /scan_history        → Scan logs
POST /verify_qr           → Verify QR code

KEYBOARD SHORTCUTS (Scanner):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
q - Quit
r - Reset verification

DATABASE TABLES:
━━━━━━━━━━━━━━━━
categories  → 6 product categories
locations   → 6 warehouse locations
products    → 16 products with QR codes
scan_logs   → History of all scans

CONFIGURATION:
━━━━━━━━━━━━━━
Edit .env file for:
- DATABASE_URL (PostgreSQL connection)
- SECRET_KEY (Flask secret)
- HOST/PORT (Server binding)

TESTING:
━━━━━━━━
python test_api.py                → Run all tests
python test_api.py verify 1/1/1   → Test specific QR
python generate_qr.py test        → Create test QR codes

COMMON ISSUES:
━━━━━━━━━━━━━━
❌ Camera error?          → Check camera index (0, 1, 2...)
❌ Database error?        → Verify PostgreSQL running
❌ Connection refused?    → Start server first
❌ QR not scanning?       → Improve lighting/focus

DEPLOYMENT:
━━━━━━━━━━━
1. Update DATABASE_URL to production PostgreSQL
2. Update SERVER_URL in robot.py to deployed URL
3. Use gunicorn for production: gunicorn app:app
4. For HTTPS streaming, use nginx or Cloudflare

SAMPLE PRODUCTS IN DATABASE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ID  Product                QR Code  Location
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1   Dove Beauty Bar        1/1/1    Shelf 1, Block A
4   Pantene Shampoo        2/4/2    Shelf 2, Block B
7   Colgate Toothpaste     3/7/3    Shelf 3, Block C
10  Tide Detergent         4/10/4   Shelf 4, Block D
13  Olay Cream             5/13/5   Shelf 5, Block A
15  L'Oreal Hair Serum     6/15/6   Shelf 6, Block B

ACCESS URLs (Local):
━━━━━━━━━━━━━━━━━━━━
Dashboard:      http://localhost:5000
Video Feed:     http://localhost:5000/video_feed
Health Check:   http://localhost:5000/health
Products List:  http://localhost:5000/products
Scan History:   http://localhost:5000/scan_history

VERIFICATION RESULTS:
━━━━━━━━━━━━━━━━━━━━━
✅ CORRECT    → Product at right location
❌ MISPLACED  → Product exists but wrong location
⚠️ NOT FOUND  → Product not in database
⚠️ INVALID    → Bad QR code format

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
For detailed documentation, see PROJECT_OVERVIEW.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

if __name__ == "__main__":
    print(__doc__)
