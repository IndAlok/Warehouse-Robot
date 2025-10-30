import sys
import os
from database import init_db
from seed_data import seed_database

# Set environment variable for UTF-8 encoding on Windows
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'

def safe_print(text):
    """Print with fallback for Unicode characters"""
    try:
        print(text)
    except UnicodeEncodeError:
        # Fallback: replace emoji with text
        text = text.replace('✅', '[OK]').replace('❌', '[ERROR]')
        print(text)

def setup():
    safe_print("=" * 50)
    safe_print("Warehouse Robot Database Setup")
    safe_print("=" * 50)
    
    try:
        safe_print("\n1. Creating database tables...")
        init_db()
        
        safe_print("\n2. Seeding database with dummy data...")
        seed_database()
        
        safe_print("\n" + "=" * 50)
        safe_print("✅ Database setup completed successfully!")
        safe_print("=" * 50)
        safe_print("\nYou can now start the server with: python server.py")
        
    except Exception as e:
        safe_print(f"\n❌ Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    setup()
