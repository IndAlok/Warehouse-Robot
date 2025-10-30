import subprocess
import sys
import os
import io

# Fix Windows console encoding for Unicode characters
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def run_command(command, description):
    print(f"\n{'='*60}")
    print(f"🔧 {description}")
    print(f"{'='*60}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        print(e.stderr)
        return False

def main():
    print("""
╔══════════════════════════════════════════════════════════╗
║     Warehouse Robot - Quick Start Installer              ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    print("\n📋 Prerequisites Check:")
    print("   ✓ Python 3.8+ installed")
    print("   ✓ PostgreSQL installed and running")
    print("   ✓ Camera connected (or available)")
    
    input("\nPress Enter to continue with installation...")
    
    if not run_command("pip install -r requirements.txt", "Installing Python packages"):
        print("\n⚠ Warning: Some packages failed to install. Continuing anyway...")
    
    print("\n" + "="*60)
    print("📊 Database Setup")
    print("="*60)
    print("\nIMPORTANT: Ensure PostgreSQL is running and database exists!")
    print("\nTo create the database, run in PostgreSQL:")
    print("   CREATE DATABASE warehouse_db;")
    
    response = input("\nIs the database ready? (y/n): ").lower()
    
    if response == 'y':
        if run_command("python setup_database.py", "Setting up database tables and seed data"):
            print("\n✅ Database setup completed successfully!")
        else:
            print("\n❌ Database setup failed. Please check your PostgreSQL connection.")
            print("   Update DATABASE_URL in .env file with correct credentials.")
            sys.exit(1)
    else:
        print("\n⚠ Skipping database setup. Run 'python setup_database.py' later.")
    
    print("\n" + "="*60)
    print("✅ Installation Complete!")
    print("="*60)
    print("\n📝 Next Steps:")
    print("\n1. Start the server:")
    print("   python server.py")
    print("   OR")
    print("   run.bat")
    print("\n2. In another terminal, start the robot scanner:")
    print("   python robot.py")
    print("   OR")
    print("   start_robot.bat")
    print("\n3. Access the video stream:")
    print("   http://localhost:5000/video_feed")
    print("\n4. View scan history:")
    print("   http://localhost:5000/scan_history")
    print("\n5. Get all products:")
    print("   http://localhost:5000/products")
    
    print("\n" + "="*60)
    print("🎯 QR Code Format: category_id/product_id/location_id")
    print("   Example: 1/1/1 (Soap product in Shelf 1, Block A)")
    print("="*60)

if __name__ == "__main__":
    main()
