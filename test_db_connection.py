import psycopg2
from config import Config
import sys

def test_connection():
    """Test PostgreSQL database connection"""
    print("="*60)
    print("DATABASE CONNECTION TEST")
    print("="*60)
    print(f"\nTesting connection to: {Config.DATABASE_URL}")
    print("(Password hidden for security)\n")
    
    try:
        # Test connection
        print("1️⃣  Attempting to connect...")
        conn = psycopg2.connect(Config.DATABASE_URL)
        print("   ✅ Connection established!\n")
        
        # Get database version
        print("2️⃣  Checking PostgreSQL version...")
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"   ✅ {version.split(',')[0]}\n")
        
        # Get database name
        print("3️⃣  Checking current database...")
        cursor.execute("SELECT current_database();")
        db_name = cursor.fetchone()[0]
        print(f"   ✅ Connected to database: {db_name}\n")
        
        # List all tables
        print("4️⃣  Checking tables...")
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()
        
        if tables:
            print(f"   ✅ Found {len(tables)} table(s):")
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table[0]};")
                count = cursor.fetchone()[0]
                print(f"      • {table[0]}: {count} records")
        else:
            print("   ⚠️  No tables found. Run 'python setup_database.py' to create tables.")
        
        print()
        
        # Test write permission
        print("5️⃣  Testing write permissions...")
        try:
            cursor.execute("CREATE TABLE IF NOT EXISTS _test_table (id SERIAL PRIMARY KEY);")
            cursor.execute("DROP TABLE _test_table;")
            conn.commit()
            print("   ✅ Write permissions OK\n")
        except Exception as e:
            print(f"   ⚠️  Write permission issue: {e}\n")
        
        cursor.close()
        conn.close()
        
        print("="*60)
        print("🎉 ALL TESTS PASSED!")
        print("="*60)
        print("\nYour database is configured correctly and ready to use.")
        print("Next steps:")
        print("  1. Run: python setup_database.py (if tables don't exist)")
        print("  2. Run: python app.py (start server)")
        print("  3. Run: python robot.py (start scanner)")
        
        return True
        
    except psycopg2.OperationalError as e:
        print(f"\n❌ CONNECTION FAILED!")
        print("="*60)
        print(f"Error: {e}\n")
        
        print("TROUBLESHOOTING STEPS:")
        print("-" * 60)
        print("1. Check PostgreSQL is running:")
        print("   Windows: Services → postgresql-x64-16 → Status")
        print("   PowerShell: Get-Service -Name postgresql*")
        print()
        print("2. Verify database exists:")
        print("   psql -U postgres")
        print("   \\l  (list databases)")
        print("   CREATE DATABASE warehouse_db;  (if not exists)")
        print()
        print("3. Check .env file settings:")
        print("   DATABASE_URL format:")
        print("   postgresql://username:password@host:port/database")
        print()
        print("4. Verify credentials:")
        print("   Username and password must match PostgreSQL setup")
        print()
        print("5. Check port 5432 is accessible:")
        print("   netstat -ano | findstr :5432")
        print()
        
        return False
        
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR!")
        print("="*60)
        print(f"Error: {e}\n")
        print("Please check your configuration and try again.")
        
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
