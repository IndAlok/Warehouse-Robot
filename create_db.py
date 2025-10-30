import os
import sqlite3
from datetime import datetime

# Ensure data directory exists
os.makedirs("data", exist_ok=True)

db_path = os.path.join("data", "warehouse_log.db")
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Create the verification_log table (same schema used by QR_detector.py)
cur.execute('''CREATE TABLE IF NOT EXISTS verification_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    product_id TEXT,
    expected_shelf TEXT,
    detected_shelf TEXT,
    status TEXT
)''')

# Insert one sample row
cur.execute(
    "INSERT INTO verification_log (timestamp, product_id, expected_shelf, detected_shelf, status) VALUES (?, ?, ?, ?, ?)",
    (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "P_SAMPLE", "SAMPLE_SHELF", "SAMPLE_SHELF", "✅ Correct")
)

conn.commit()
conn.close()

print(f"Created {db_path} with one sample row.")
