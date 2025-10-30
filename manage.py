import os
import sys
import subprocess
import time
import io

# Fix Windows console encoding for Unicode characters
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60 + "\n")

def run_command(command, description=""):
    if description:
        print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stderr:
            print(e.stderr)
        return False

def install_dependencies():
    clear_screen()
    print_header("Installing Dependencies")
    
    print("📦 Installing Python packages from requirements.txt...\n")
    if run_command("pip install -r requirements.txt", "Installing packages"):
        print("\n✅ Dependencies installed successfully!")
    else:
        print("\n⚠ Some packages may have failed to install.")
    
    input("\nPress Enter to continue...")

def setup_database():
    clear_screen()
    print_header("Database Setup")
    
    print("📊 Setting up PostgreSQL database...\n")
    print("IMPORTANT: Make sure PostgreSQL is installed and running!")
    print("\nDefault database name: warehouse_db")
    print("Default credentials: postgres/postgres\n")
    
    response = input("Have you created the database 'warehouse_db'? (y/n): ").lower()
    
    if response == 'y':
        if run_command("python setup_database.py", "Initializing database"):
            print("\n✅ Database setup completed!")
        else:
            print("\n❌ Database setup failed!")
    else:
        print("\nPlease create the database first:")
        print("  1. Open pgAdmin or psql")
        print("  2. Run: CREATE DATABASE warehouse_db;")
        print("  3. Run this script again")
    
    input("\nPress Enter to continue...")

def generate_qr_codes():
    clear_screen()
    print_header("Generate QR Codes")
    
    print("1. Generate QR codes for all products in database")
    print("2. Generate test QR codes (with misplaced examples)")
    print("3. Back to main menu")
    
    choice = input("\nSelect option (1-3): ").strip()
    
    if choice == '1':
        run_command("python generate_qr.py", "Generating product QR codes")
    elif choice == '2':
        run_command("python generate_qr.py test", "Generating test QR codes")
    
    input("\nPress Enter to continue...")

def start_server():
    clear_screen()
    print_header("Starting Server")
    
    print("🚀 Starting Flask server with web dashboard...\n")
    print("Dashboard will be available at: http://localhost:5000")
    print("Press Ctrl+C to stop the server\n")
    
    input("Press Enter to start server...")
    
    try:
        subprocess.run("python app.py", shell=True)
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped.")
        time.sleep(2)

def start_robot():
    clear_screen()
    print_header("Starting Robot Scanner")
    
    print("🤖 Starting warehouse robot QR scanner...\n")
    print("Make sure the server is running in another terminal!")
    print("Press 'q' in the scanner window to quit\n")
    
    input("Press Enter to start scanner...")
    
    try:
        subprocess.run("python robot.py", shell=True)
    except KeyboardInterrupt:
        print("\n\n🛑 Scanner stopped.")
        time.sleep(2)

def test_api():
    clear_screen()
    print_header("API Testing")
    
    print("Running comprehensive API test suite...\n")
    print("Make sure the server is running!\n")
    
    input("Press Enter to start tests...")
    
    run_command("python test_api.py", "Running API tests")
    
    input("\nPress Enter to continue...")

def view_configuration():
    clear_screen()
    print_header("Configuration")
    
    print("📄 Current .env configuration:\n")
    
    try:
        with open('.env', 'r') as f:
            print(f.read())
    except FileNotFoundError:
        print("⚠ .env file not found!")
        print("\nCreating from .env.example...")
        try:
            with open('.env.example', 'r') as f:
                content = f.read()
            with open('.env', 'w') as f:
                f.write(content)
            print("✅ Created .env file from template")
        except:
            print("❌ Failed to create .env file")
    
    input("\nPress Enter to continue...")

def show_help():
    clear_screen()
    print_header("Help & Documentation")
    
    print("""
📚 WAREHOUSE ROBOT SYSTEM

OVERVIEW:
  This system uses computer vision to scan QR codes on warehouse shelves
  and verify products are in their correct locations using a PostgreSQL database.

COMPONENTS:
  • robot.py    - QR scanner with camera integration
  • app.py      - Web server with dashboard and API
  • database.py - PostgreSQL ORM models

WORKFLOW:
  1. Robot scans QR code on shelf
  2. Sends code to server for verification
  3. Server checks database for correct location
  4. Returns result (correct/misplaced/not found)
  5. Logs scan in database

QR CODE FORMAT:
  category_id/product_id/location_id
  
  Example: "1/2/1" means:
    - Category 1 (Soap)
    - Product 2 (Lux Velvet Touch Soap)
    - Location 1 (Shelf 1 in Block A)

API ENDPOINTS:
  GET  /                     - Web dashboard
  GET  /video_feed           - Live video stream
  GET  /health               - Health check
  GET  /products             - List all products
  GET  /scan_history         - Get scan logs
  POST /verify_qr            - Verify QR code
  POST /upload_frame         - Upload video frame

DATABASE TABLES:
  • categories  - Product categories
  • locations   - Warehouse shelf locations
  • products    - Product inventory
  • scan_logs   - QR scan history

KEYBOARD SHORTCUTS (in scanner):
  q - Quit scanner
  r - Reset current verification

    """)
    
    input("Press Enter to continue...")

def main_menu():
    while True:
        clear_screen()
        print("""
╔══════════════════════════════════════════════════════════╗
║       Warehouse Robot Management Console                ║
╚══════════════════════════════════════════════════════════╝

  1. Install Dependencies
  2. Setup Database (create tables & seed data)
  3. Generate QR Codes
  4. Start Server (with web dashboard)
  5. Start Robot Scanner
  6. Test API
  7. View Configuration
  8. Help & Documentation
  9. Exit

        """)
        
        choice = input("Select option (1-9): ").strip()
        
        if choice == '1':
            install_dependencies()
        elif choice == '2':
            setup_database()
        elif choice == '3':
            generate_qr_codes()
        elif choice == '4':
            start_server()
        elif choice == '5':
            start_robot()
        elif choice == '6':
            test_api()
        elif choice == '7':
            view_configuration()
        elif choice == '8':
            show_help()
        elif choice == '9':
            print("\n👋 Goodbye!\n")
            sys.exit(0)
        else:
            print("\n❌ Invalid option. Please select 1-9.")
            time.sleep(1)

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n\n👋 Exiting...\n")
        sys.exit(0)
