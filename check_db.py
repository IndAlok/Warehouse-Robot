import sqlite3
import pprint

DB_PATH = "data/warehouse_log.db"

def main(limit=10):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Count rows
    cur.execute("SELECT COUNT(*) FROM verification_log")
    total = cur.fetchone()[0]
    print(f"Total rows in verification_log: {total}\n")

    # Show latest rows (by id desc)
    cur.execute("SELECT id, timestamp, product_id, expected_shelf, detected_shelf, status FROM verification_log ORDER BY id DESC LIMIT ?", (limit,))
    rows = cur.fetchall()

    if rows:
        print(f"Showing up to {limit} most recent rows:")
        p = pprint.PrettyPrinter(indent=2)
        p.pprint(rows)
    else:
        print("No rows found in verification_log.")

    conn.close()

if __name__ == '__main__':
    main()
