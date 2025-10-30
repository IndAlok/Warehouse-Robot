"""
═══════════════════════════════════════════════════════════════════
    POSTGRESQMETHOD 1: Using psql Command Line
──────────────────────────────────

For Native PostgreSQL Installation:
────────────────────────────────────
Step 1: Connect to PostgreSQL
    psql -U postgres
    
    • Enter password when prompted (set during installation)

Step 2: Create Database
    CREATE DATABASE warehouse_db;

Step 3: Verify Creation
    \l                         -- List all databases
    \c warehouse_db            -- Connect to warehouse_db

StepStep 6: Verify Database
    For Native Installation:
        psql -U postgres -d warehouse_db
    
    For Docker Installation:
        docker exec -it warehouse-postgres psql -U postgres -d warehouse_db
    
    Run queries:
        \dt                           -- List tables
        SELECT COUNT(*) FROM products;  -- Should return 16
        SELECT * FROM categories;       -- View all categories
        \q                            -- Exit
    \q                         -- Quit psql


For Docker Installation:
────────────────────────
Step 1: Connect to PostgreSQL container
    docker exec -it warehouse-postgres psql -U postgres
    
    • No password needed (using default 'postgres' user)

Step 2: Create Database
    CREATE DATABASE warehouse_db;

Step 3: Verify Creation
    \l                         -- List all databases
    \c warehouse_db            -- Connect to warehouse_db

Step 4: Exit
    \q                         -- Quit psql

Alternative - One-liner to connect to specific database:
    docker exec -it warehouse-postgres psql -U postgres -d warehouse_db ENVIRONMENT GUIDE
═══════════════════════════════════════════════════════════════════

TABLE OF CONTENTS:
1. PostgreSQL Installation
2. Database Creation
3. User & Permission Setup
4. Environment Variables Explained
5. Connection String Format
6. Local Development Setup
7. Cloud Database Setup (Production)
8. Testing Database Connection
9. Common Issues & Solutions
10. Security Best Practices


═══════════════════════════════════════════════════════════════════
1. POSTGRESQL INSTALLATION
═══════════════════════════════════════════════════════════════════

WINDOWS (Your Current System):
────────────────────────────────

Option A: Official PostgreSQL Installer
┌─────────────────────────────────────────────────────────────────┐
│ 1. Download from: https://www.postgresql.org/download/windows/ │
│ 2. Run the installer (postgresql-16.x-windows-x64.exe)         │
│ 3. Installation wizard steps:                                  │
│    • Installation Directory: C:\\Program Files\\PostgreSQL\\16    │
│    • Select Components:                                        │
│      ✓ PostgreSQL Server                                       │
│      ✓ pgAdmin 4 (GUI tool)                                    │
│      ✓ Command Line Tools                                      │
│    • Data Directory: C:\\Program Files\\PostgreSQL\\16\\data      │
│    • Password: Set a strong password for 'postgres' user      │
│    • Port: 5432 (default)                                      │
│    • Locale: Default                                           │
│ 4. Click 'Next' and 'Finish'                                   │
│ 5. PostgreSQL service starts automatically                     │
└─────────────────────────────────────────────────────────────────┘

Option B: Using Docker (Recommended for Development)
┌─────────────────────────────────────────────────────────────────┐
│ 1. Install Docker Desktop for Windows                          │
│ 2. Run PostgreSQL container:                                   │
│                                                                 │
│    docker run --name warehouse-postgres -d \\                   │
│      -e POSTGRES_PASSWORD=postgres \\                           │
│      -e POSTGRES_DB=warehouse_db \\                             │
│      -p 5432:5432 \\                                            │
│      postgres:16                                               │
│                                                                 │
│ 3. PostgreSQL is now running on localhost:5432                 │
│ 4. To stop: docker stop warehouse-postgres                     │
│ 5. To start: docker start warehouse-postgres                   │
│ 6. To remove: docker rm -f warehouse-postgres                  │
└─────────────────────────────────────────────────────────────────┘

VERIFY INSTALLATION:
────────────────────

For Native Installation:
    Open PowerShell and run:
        psql --version
    
    Expected output:
        psql (PostgreSQL) 16.x

For Docker Installation:
    Check container status:
        docker ps | findstr warehouse-postgres
    
    Connect to PostgreSQL:
        docker exec -it warehouse-postgres psql -U postgres
    
    Expected output:
        psql (16.x)
        Type "help" for help.
        postgres=#


═══════════════════════════════════════════════════════════════════
2. DATABASE CREATION
═══════════════════════════════════════════════════════════════════

METHOD 1: Using psql Command Line
──────────────────────────────────

Step 1: Connect to PostgreSQL
    psql -U postgres
    
    • Enter password when prompted (set during installation)

Step 2: Create Database
    CREATE DATABASE warehouse_db;

Step 3: Verify Creation
    \\l                         -- List all databases
    \\c warehouse_db            -- Connect to warehouse_db

Step 4: Exit
    \\q                         -- Quit psql


METHOD 2: Using pgAdmin 4 (GUI)
────────────────────────────────

Step 1: Open pgAdmin 4
    • Installed with PostgreSQL
    • Default: http://localhost:5050 or desktop app

Step 2: Connect to Server
    • Expand 'Servers' → 'PostgreSQL 16'
    • Enter master password

Step 3: Create Database
    • Right-click 'Databases' → 'Create' → 'Database'
    • Database name: warehouse_db
    • Owner: postgres
    • Click 'Save'

Step 4: Verify
    • Database appears in left sidebar under 'Databases'


METHOD 3: Using Python Script (Automated)
──────────────────────────────────────────

Create file: create_database.py
────────────────────────────────
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Connect to default 'postgres' database
conn = psycopg2.connect(
    host="localhost",
    port=5432,
    user="postgres",
    password="postgres"  # Change to your password
)
conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

# Create database
cursor = conn.cursor()
cursor.execute("SELECT 1 FROM pg_database WHERE datname='warehouse_db'")
exists = cursor.fetchone()

if not exists:
    cursor.execute("CREATE DATABASE warehouse_db")
    print("✅ Database 'warehouse_db' created successfully!")
else:
    print("ℹ️  Database 'warehouse_db' already exists.")

cursor.close()
conn.close()

Run:
    python create_database.py


═══════════════════════════════════════════════════════════════════
3. USER & PERMISSION SETUP
═══════════════════════════════════════════════════════════════════

CREATING A DEDICATED USER (Recommended for Production)
───────────────────────────────────────────────────────

Step 1: Connect as superuser
    psql -U postgres

Step 2: Create new user
    CREATE USER warehouse_user WITH PASSWORD 'secure_password_123';

Step 3: Grant privileges
    GRANT ALL PRIVILEGES ON DATABASE warehouse_db TO warehouse_user;

Step 4: Connect to database and grant schema permissions
    \\c warehouse_db
    GRANT ALL ON SCHEMA public TO warehouse_user;
    GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO warehouse_user;
    GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO warehouse_user;

Step 5: Make privileges permanent for future tables
    ALTER DEFAULT PRIVILEGES IN SCHEMA public 
        GRANT ALL ON TABLES TO warehouse_user;
    ALTER DEFAULT PRIVILEGES IN SCHEMA public 
        GRANT ALL ON SEQUENCES TO warehouse_user;

Step 6: Verify
    \\du                        -- List all users
    \\dp                        -- List table permissions


USING DEFAULT 'postgres' USER (Simpler for Development)
────────────────────────────────────────────────────────
For local development, you can use the default 'postgres' user:
    • Username: postgres
    • Password: (set during installation)
    • Has all permissions by default


═══════════════════════════════════════════════════════════════════
4. ENVIRONMENT VARIABLES EXPLAINED
═══════════════════════════════════════════════════════════════════

YOUR .env FILE STRUCTURE:
─────────────────────────

DATABASE_URL=postgresql://username:password@host:port/database_name
SECRET_KEY=your-secret-key-here
FLASK_ENV=development
HOST=0.0.0.0
PORT=5000


DETAILED PARAMETER EXPLANATION:
────────────────────────────────

┌─────────────────────────────────────────────────────────────────┐
│ DATABASE_URL                                                    │
├─────────────────────────────────────────────────────────────────┤
│ Purpose: PostgreSQL connection string                          │
│ Format:  postgresql://[user]:[password]@[host]:[port]/[dbname] │
│                                                                 │
│ Components:                                                     │
│   • postgresql:// → Database protocol (required)                │
│   • user          → Database username                           │
│   • password      → Database password                           │
│   • host          → Database server address                     │
│   • port          → Database port (default: 5432)               │
│   • dbname        → Database name                               │
│                                                                 │
│ Examples:                                                       │
│   Local (postgres user):                                        │
│     postgresql://postgres:postgres@localhost:5432/warehouse_db │
│                                                                 │
│   Local (custom user):                                          │
│     postgresql://warehouse_user:mypass@localhost:5432/warehouse_db │
│                                                                 │
│   Docker container:                                             │
│     postgresql://postgres:postgres@127.0.0.1:5432/warehouse_db │
│                                                                 │
│   Remote server:                                                │
│     postgresql://user:pass@192.168.1.100:5432/warehouse_db    │
│                                                                 │
│   Heroku (auto-provided):                                       │
│     postgres://user:pass@ec2-xxx.compute.amazonaws.com:5432/db │
│                                                                 │
│   Supabase:                                                     │
│     postgresql://postgres:pass@db.xxx.supabase.co:5432/postgres │
│                                                                 │
│   Special characters in password:                               │
│     Use URL encoding:                                           │
│     @ → %40, : → %3A, / → %2F, ? → %3F, # → %23               │
│     Example password "p@ss:w/rd" becomes "p%40ss%3Aw%2Frd"    │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ SECRET_KEY                                                      │
├─────────────────────────────────────────────────────────────────┤
│ Purpose: Flask session encryption and security                 │
│ Type:    String (random, unpredictable)                        │
│ Length:  Minimum 32 characters (longer is better)              │
│                                                                 │
│ Used For:                                                       │
│   • Session cookie signing                                      │
│   • CSRF token generation                                       │
│   • Cryptographic operations                                    │
│                                                                 │
│ Development Example:                                            │
│   SECRET_KEY=dev-secret-key-change-in-production               │
│                                                                 │
│ Production Example:                                             │
│   SECRET_KEY=9f3a8b2c1d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e │
│                                                                 │
│ Generate Secure Key (Python):                                   │
│   import secrets                                                │
│   print(secrets.token_hex(32))                                  │
│                                                                 │
│ Generate Secure Key (PowerShell):                               │
│   [System.Convert]::ToBase64String(                            │
│     [System.Security.Cryptography.RandomNumberGenerator]::     │
│     GetBytes(32))                                              │
│                                                                 │
│ ⚠️  IMPORTANT:                                                  │
│   • Never commit production secret key to Git                   │
│   • Use different keys for dev/staging/production               │
│   • Changing key invalidates all existing sessions              │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ FLASK_ENV                                                       │
├─────────────────────────────────────────────────────────────────┤
│ Purpose: Set Flask application environment mode                │
│ Type:    String                                                 │
│                                                                 │
│ Values:                                                         │
│   development → Debug mode ON, auto-reload, verbose errors     │
│   production  → Debug mode OFF, optimized, minimal logs        │
│                                                                 │
│ Development (FLASK_ENV=development):                            │
│   ✓ Auto-reloads when code changes                             │
│   ✓ Detailed error pages with stack traces                     │
│   ✓ Interactive debugger in browser                            │
│   ⚠️  NOT secure for public deployment                         │
│                                                                 │
│ Production (FLASK_ENV=production):                              │
│   ✓ No auto-reload (requires restart)                          │
│   ✓ Generic error pages (no sensitive info)                    │
│   ✓ Better performance                                          │
│   ✓ Secure for public access                                   │
│                                                                 │
│ Current Project Setting:                                        │
│   FLASK_ENV=development  (change to 'production' when deploying)│
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ HOST                                                            │
├─────────────────────────────────────────────────────────────────┤
│ Purpose: Network interface Flask server binds to               │
│ Type:    IP Address or hostname                                │
│                                                                 │
│ Values:                                                         │
│   127.0.0.1 or localhost → Only local machine can access       │
│   0.0.0.0                → All network interfaces (LAN/WAN)     │
│   192.168.x.x            → Specific network interface           │
│                                                                 │
│ HOST=127.0.0.1 (localhost):                                     │
│   • Server only accessible from same computer                   │
│   • Access: http://127.0.0.1:5000 or http://localhost:5000    │
│   • Other devices on network CANNOT access                      │
│   • Most secure for development                                 │
│                                                                 │
│ HOST=0.0.0.0 (all interfaces):                                  │
│   • Server accessible from any network interface                │
│   • Access from same PC: http://localhost:5000                 │
│   • Access from LAN: http://192.168.1.x:5000                   │
│   • Robot on different device can connect                       │
│   • Required for production deployment                          │
│                                                                 │
│ Current Project Setting:                                        │
│   HOST=0.0.0.0  (allows network access for robot connection)   │
│                                                                 │
│ Use Cases:                                                      │
│   • Robot and server on same PC → 127.0.0.1 OK                 │
│   • Robot on different device → 0.0.0.0 required                │
│   • Cloud deployment → 0.0.0.0 required                         │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ PORT                                                            │
├─────────────────────────────────────────────────────────────────┤
│ Purpose: TCP port number Flask server listens on               │
│ Type:    Integer (1-65535)                                      │
│                                                                 │
│ Common Ports:                                                   │
│   5000  → Flask default, used in this project                   │
│   8000  → Alternative development port                          │
│   8080  → Common alternative                                    │
│   80    → HTTP standard (requires admin/root)                   │
│   443   → HTTPS standard (requires admin/root)                  │
│                                                                 │
│ PORT=5000:                                                      │
│   • Standard Flask development port                             │
│   • No admin privileges needed                                  │
│   • Access: http://localhost:5000                              │
│   • Used throughout this project                                │
│                                                                 │
│ Restrictions:                                                   │
│   • Ports 1-1023 require admin/root privileges                  │
│   • Port must not be in use by another application              │
│   • Firewall may block certain ports                            │
│                                                                 │
│ Current Project Setting:                                        │
│   PORT=5000                                                     │
│                                                                 │
│ Checking if port is in use (PowerShell):                        │
│   netstat -ano | findstr :5000                                 │
│                                                                 │
│ Changing Port:                                                  │
│   1. Update PORT in .env                                        │
│   2. Update SERVER_URL in robot.py                              │
│   3. Restart server                                             │
└─────────────────────────────────────────────────────────────────┘


═══════════════════════════════════════════════════════════════════
5. CONNECTION STRING FORMAT BREAKDOWN
═══════════════════════════════════════════════════════════════════

ANATOMY OF DATABASE_URL:
─────────────────────────

postgresql://postgres:mypassword@localhost:5432/warehouse_db
│         │   │      │ │          │ │        │ │             │
│         │   │      │ │          │ │        │ │             └─ Database name
│         │   │      │ │          │ │        │ └─────────────── Port number
│         │   │      │ │          │ └────────┴───────────────── Host address
│         │   │      │ └──────────┴──────────────────────────── Password
│         │   └─────┴─────────────────────────────────────────── Username
│         └─────────────────────────────────────────────────────── Separator
└───────────────────────────────────────────────────────────────── Protocol


COMPONENT DETAILS:
──────────────────

1. Protocol: postgresql:// or postgres://
   Both work, postgresql:// is more explicit

2. Username: 
   • Default: postgres (superuser)
   • Custom: warehouse_user (created separately)
   • Case-sensitive on some systems

3. Password:
   • Set during PostgreSQL installation
   • Or when creating user
   • Special characters must be URL-encoded
   • Empty password: leave blank (not recommended)
     Example: postgresql://postgres:@localhost:5432/warehouse_db

4. Host:
   • localhost or 127.0.0.1 → Local machine
   • 192.168.x.x → Local network IP
   • domain.com → Remote server domain
   • Docker: host.docker.internal (from container to host)

5. Port:
   • Default PostgreSQL: 5432
   • Can be omitted if using default
   • Example: postgresql://user:pass@localhost/warehouse_db
   • Custom port must be specified

6. Database Name:
   • Must exist before connecting
   • Case-sensitive
   • Created with CREATE DATABASE command


VARIATIONS & EXAMPLES:
──────────────────────

Minimal (using defaults):
    postgresql://postgres@localhost/warehouse_db
    (assumes password-less connection, default port)

With explicit port:
    postgresql://postgres:pass@localhost:5432/warehouse_db

IPv6 address:
    postgresql://postgres:pass@[::1]:5432/warehouse_db

With schema:
    postgresql://postgres:pass@localhost/warehouse_db?schema=public

With SSL:
    postgresql://postgres:pass@host:5432/db?sslmode=require

Multiple connection parameters:
    postgresql://postgres:pass@host:5432/db?sslmode=require&connect_timeout=10


═══════════════════════════════════════════════════════════════════
6. LOCAL DEVELOPMENT SETUP (Step-by-Step)
═══════════════════════════════════════════════════════════════════

COMPLETE SETUP PROCESS:
────────────────────────

Step 1: Install PostgreSQL
    ✓ Download from https://www.postgresql.org/download/windows/
    ✓ Run installer
    ✓ Set postgres user password: "postgres" (or your choice)
    ✓ Port: 5432
    ✓ Complete installation

Step 2: Verify Installation
    Open PowerShell:
        psql --version
    
    Expected: psql (PostgreSQL) 16.x

Step 3: Create Database
    Option A - Command Line:
        psql -U postgres
        Password: [enter your password]
        
        CREATE DATABASE warehouse_db;
        \\l                    -- Verify creation
        \\q                    -- Exit

    Option B - pgAdmin:
        Open pgAdmin 4
        → Servers → PostgreSQL 16
        → Right-click Databases → Create → Database
        → Name: warehouse_db
        → Save

Step 4: Configure .env File
    Open: c:\\Users\\Admin\\Desktop\\warehouse-robot\\.env
    
    Set values:
        DATABASE_URL=postgresql://postgres:postgres@localhost:5432/warehouse_db
        SECRET_KEY=dev-secret-key-change-in-production
        FLASK_ENV=development
        HOST=0.0.0.0
        PORT=5000
    
    ⚠️  Replace "postgres:postgres" with your actual username:password

Step 5: Initialize Database Tables
    cd c:\\Users\\Admin\\Desktop\\warehouse-robot
    python setup_database.py
    
    Expected output:
        ✅ Creating database tables...
        ✅ Seeding database...
        ✅ Successfully seeded database with:
           - 6 categories
           - 6 locations
           - 16 products

Step 6: Verify Database
    psql -U postgres -d warehouse_db
    
    Run queries:
        \\dt                           -- List tables
        SELECT COUNT(*) FROM products;  -- Should return 16
        SELECT * FROM categories;       -- View all categories
        \\q                            -- Exit

Step 7: Test Connection from Python
    Create test_connection.py:
        from database import get_session, Product
        
        session = get_session()
        try:
            count = session.query(Product).count()
            print(f"✅ Connected! Found {count} products")
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            session.close()
    
    Run:
        python test_connection.py
    
    Expected:
        ✅ Connected! Found 16 products


═══════════════════════════════════════════════════════════════════
7. CLOUD DATABASE SETUP (Production)
═══════════════════════════════════════════════════════════════════

OPTION 1: HEROKU POSTGRES
──────────────────────────

Step 1: Create Heroku Account
    • Go to: https://www.heroku.com
    • Sign up for free account

Step 2: Install Heroku CLI
    • Download: https://devcenter.heroku.com/articles/heroku-cli
    • Install for Windows

Step 3: Login
    heroku login

Step 4: Create App
    heroku create warehouse-robot-app

Step 5: Add PostgreSQL
    heroku addons:create heroku-postgresql:essential-0
    
    (Free tier available with verification)

Step 6: Get Database URL
    heroku config:get DATABASE_URL -a warehouse-robot-app
    
    Copy the URL (looks like):
    postgres://user:pass@ec2-xx-xx-xx-xx.compute.amazonaws.com:5432/dbname

Step 7: Update .env for Production
    DATABASE_URL=[paste Heroku URL here]
    SECRET_KEY=[generate secure key]
    FLASK_ENV=production
    HOST=0.0.0.0
    PORT=5000


OPTION 2: SUPABASE (Free Tier Available)
─────────────────────────────────────────

Step 1: Create Supabase Account
    • Go to: https://supabase.com
    • Sign up with GitHub/Google

Step 2: Create New Project
    • Click "New Project"
    • Name: warehouse-robot
    • Database Password: [strong password]
    • Region: Choose closest to you
    • Click "Create Project"

Step 3: Get Connection String
    • Go to Project Settings → Database
    • Find "Connection String" → "URI"
    • Copy connection string:
      postgresql://postgres:[YOUR-PASSWORD]@db.xxx.supabase.co:5432/postgres

Step 4: Update .env
    DATABASE_URL=postgresql://postgres:yourpass@db.xxx.supabase.co:5432/postgres


OPTION 3: RAILWAY (Simple & Free)
──────────────────────────────────

Step 1: Create Railway Account
    • Go to: https://railway.app
    • Sign up with GitHub

Step 2: New Project
    • Click "New Project"
    • Select "Provision PostgreSQL"

Step 3: Get Connection URL
    • Click database → Connect
    • Copy "Postgres Connection URL"

Step 4: Update .env
    DATABASE_URL=[paste Railway URL]


OPTION 4: NEON (Serverless Postgres)
─────────────────────────────────────

Step 1: Create Account
    • Go to: https://neon.tech
    • Sign up

Step 2: Create Project
    • New Project → warehouse-robot
    • Select region

Step 3: Get Connection String
    • Dashboard → Connection Details
    • Copy connection string

Step 4: Update .env
    DATABASE_URL=[paste Neon URL]


═══════════════════════════════════════════════════════════════════
8. TESTING DATABASE CONNECTION
═══════════════════════════════════════════════════════════════════

TEST #1: psql Command Line
───────────────────────────

For Native Installation:
    psql "postgresql://postgres:postgres@localhost:5432/warehouse_db"

For Docker Installation:
    docker exec -it warehouse-postgres psql -U postgres -d warehouse_db

Success:
    warehouse_db=#

Error (Native):
    psql: error: connection to server at "localhost" (::1), port 5432 failed

Error (Docker):
    Error response from daemon: Container is not running
    → Solution: docker start warehouse-postgres


TEST #2: Python Script
──────────────────────

Create: test_db_connection.py
──────────────────────────────
import psycopg2
from config import Config

try:
    conn = psycopg2.connect(Config.DATABASE_URL)
    print("✅ Database connection successful!")
    
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    version = cursor.fetchone()
    print(f"📊 PostgreSQL version: {version[0]}")
    
    cursor.close()
    conn.close()
    
except psycopg2.OperationalError as e:
    print(f"❌ Connection failed: {e}")
    print("\\nTroubleshooting:")
    print("1. Check PostgreSQL is running")
    print("2. Verify DATABASE_URL in .env")
    print("3. Check username and password")
    print("4. Ensure database 'warehouse_db' exists")
except Exception as e:
    print(f"❌ Unexpected error: {e}")

Run:
    python test_db_connection.py


TEST #3: Using Project's Database Module
─────────────────────────────────────────

Create: test_project_db.py
──────────────────────────
from database import get_session, Product, Category, Location

def test_database():
    session = get_session()
    
    try:
        # Test 1: Count products
        product_count = session.query(Product).count()
        print(f"✅ Products in database: {product_count}")
        
        # Test 2: Count categories
        category_count = session.query(Category).count()
        print(f"✅ Categories in database: {category_count}")
        
        # Test 3: Count locations
        location_count = session.query(Location).count()
        print(f"✅ Locations in database: {location_count}")
        
        # Test 4: Get a sample product
        product = session.query(Product).first()
        if product:
            print(f"✅ Sample product: {product.name} (QR: {product.qr_code})")
        
        # Test 5: Query with relationships
        product_with_details = session.query(Product).filter_by(id=1).first()
        if product_with_details:
            print(f"✅ Product: {product_with_details.name}")
            print(f"   Category: {product_with_details.category.name}")
            print(f"   Location: {product_with_details.location.full_location}")
        
        print("\\n🎉 All database tests passed!")
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    test_database()

Run:
    python test_project_db.py


═══════════════════════════════════════════════════════════════════
9. COMMON ISSUES & SOLUTIONS
═══════════════════════════════════════════════════════════════════

ISSUE 1: "Connection refused"
──────────────────────────────
Error:
    psycopg2.OperationalError: connection to server at "localhost" 
    (127.0.0.1), port 5432 failed: Connection refused

Solutions:
    1. Check PostgreSQL is running:
       Windows Services → postgresql-x64-16 → Status: Running
       
       Or PowerShell:
       Get-Service -Name postgresql*
    
    2. Start PostgreSQL:
       net start postgresql-x64-16
       
       Or use pgAdmin Service tab
    
    3. Check port:
       netstat -ano | findstr :5432


ISSUE 2: "Database does not exist"
───────────────────────────────────
Error:
    psycopg2.OperationalError: database "warehouse_db" does not exist

Solution:
    psql -U postgres
    CREATE DATABASE warehouse_db;
    \\q


ISSUE 3: "Password authentication failed"
──────────────────────────────────────────
Error:
    psycopg2.OperationalError: password authentication failed for user "postgres"

Solutions:
    1. Check password in .env matches PostgreSQL
    
    2. Reset postgres password:
       psql -U postgres
       ALTER USER postgres PASSWORD 'newpassword';
    
    3. Check pg_hba.conf authentication method:
       Location: C:\\Program Files\\PostgreSQL\\16\\data\\pg_hba.conf
       Change: md5 → trust (for local dev only!)


ISSUE 4: "Role does not exist"
───────────────────────────────
Error:
    psycopg2.OperationalError: role "warehouse_user" does not exist

Solution:
    psql -U postgres
    CREATE USER warehouse_user WITH PASSWORD 'password';
    GRANT ALL PRIVILEGES ON DATABASE warehouse_db TO warehouse_user;


ISSUE 5: "Permission denied"
─────────────────────────────
Error:
    psycopg2.ProgrammingError: permission denied for table products

Solution:
    psql -U postgres -d warehouse_db
    GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO warehouse_user;
    GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO warehouse_user;


ISSUE 6: "Port already in use"
───────────────────────────────
Error:
    OSError: [WinError 10048] Only one usage of each socket address

Solution:
    1. Find process using port:
       netstat -ano | findstr :5432
    
    2. Kill process:
       taskkill /PID [process_id] /F
    
    3. Or change PostgreSQL port in postgresql.conf


ISSUE 7: SQLAlchemy connection pool errors
───────────────────────────────────────────
Error:
    sqlalchemy.exc.TimeoutError: QueuePool limit of size 5 overflow 10 reached

Solution:
    Update database.py engine configuration:
    
    engine = create_engine(
        Config.DATABASE_URL,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        pool_recycle=3600
    )


═══════════════════════════════════════════════════════════════════
10. SECURITY BEST PRACTICES
═══════════════════════════════════════════════════════════════════

FOR DEVELOPMENT:
────────────────
✓ Use localhost/127.0.0.1 for DATABASE_URL host
✓ Simple password OK (e.g., "postgres")
✓ Default postgres user acceptable
✓ FLASK_ENV=development
✓ Commit .env.example, ignore .env


FOR PRODUCTION:
───────────────
✓ Use SSL connection: ?sslmode=require in DATABASE_URL
✓ Strong passwords (min 16 chars, mixed case, numbers, symbols)
✓ Dedicated database user (not postgres superuser)
✓ FLASK_ENV=production
✓ Never commit actual .env file to Git
✓ Use environment variables on hosting platform
✓ Regularly rotate SECRET_KEY
✓ Enable PostgreSQL authentication logging
✓ Use connection pooling
✓ Set up database backups
✓ Monitor connection attempts
✓ Use firewall rules to restrict database access
✓ Keep PostgreSQL updated


PASSWORD SECURITY:
──────────────────
❌ BAD:  password123
❌ BAD:  admin
❌ BAD:  warehouse

✅ GOOD: Kp9$mN2#vL8@xR5!qT1
✅ GOOD: Use password manager generated passwords

Generate secure password (PowerShell):
    Add-Type -AssemblyName System.Web
    [System.Web.Security.Membership]::GeneratePassword(20, 5)


CONNECTION STRING SECURITY:
───────────────────────────
❌ Hardcoded in Python files
❌ Committed to Git
❌ Shared via email/chat

✅ In .env file (gitignored)
✅ Environment variables on server
✅ Secret management service (AWS Secrets Manager, etc.)


.gitignore MUST INCLUDE:
────────────────────────
.env
*.log
__pycache__/
*.pyc
.venv/
venv/


═══════════════════════════════════════════════════════════════════
SUMMARY - QUICK SETUP CHECKLIST
═══════════════════════════════════════════════════════════════════

NATIVE INSTALLATION:
□ 1. Install PostgreSQL
□ 2. Start PostgreSQL service
□ 3. Create database: psql -U postgres -c "CREATE DATABASE warehouse_db;"
□ 4. Configure .env file:
     DATABASE_URL=postgresql://postgres:yourpass@localhost:5432/warehouse_db
     SECRET_KEY=generate-secure-random-key
     FLASK_ENV=development
     HOST=0.0.0.0
     PORT=5000
□ 5. Run: python setup_database.py
□ 6. Test: python test_db_connection.py
□ 7. Start server: python app.py
□ 8. Verify: http://localhost:5000

DOCKER INSTALLATION (CURRENT SETUP):
□ 1. Install Docker Desktop
□ 2. Start Docker Desktop
□ 3. Run container: docker start warehouse-postgres
□ 4. Create database: docker exec -it warehouse-postgres psql -U postgres -c "CREATE DATABASE warehouse_db;"
□ 5. Configure .env file:
     DATABASE_URL=postgresql://postgres:postgres@localhost:5432/warehouse_db
     SECRET_KEY=dev-secret-key-change-in-production
     FLASK_ENV=development
     HOST=0.0.0.0
     PORT=5000
□ 6. Run: python setup_database.py
□ 7. Test: python test_db_connection.py
□ 8. Start server: python app.py
□ 9. Verify: http://localhost:5000

═══════════════════════════════════════════════════════════════════

For more help, see:
• PostgreSQL Docs: https://www.postgresql.org/docs/
• Flask-SQLAlchemy: https://flask-sqlalchemy.palletsprojects.com/
• Heroku Postgres: https://devcenter.heroku.com/articles/heroku-postgresql

═══════════════════════════════════════════════════════════════════
"""

if __name__ == "__main__":
    print(__doc__)
