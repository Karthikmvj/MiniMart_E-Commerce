import sqlite3
import os

db_path = 'c:/Users/Vijay/MiniMart/db.sqlite3'
print("Checking database at:", db_path)
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # List tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [t[0] for t in cursor.fetchall()]
    print("Tables:")
    print(", ".join(tables))
    
    # Inspect store_order table schema
    if "store_order" in tables:
        print("\nstore_order schema:")
        cursor.execute("PRAGMA table_info(store_order);")
        for col in cursor.fetchall():
            print(col)
            
    conn.close()
else:
    print("Database not found.")
