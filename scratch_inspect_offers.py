import sqlite3
import os

db_path = 'c:/Users/Vijay/MiniMart/db.sqlite3'
print("Checking database at:", db_path)
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if store_offer exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='store_offer';")
    if cursor.fetchone():
        cursor.execute("PRAGMA table_info(store_offer);")
        columns = [col[1] for col in cursor.fetchall()]
        print("Offer Columns:", columns)
        
        cursor.execute("SELECT * FROM store_offer;")
        offers = cursor.fetchall()
        print(f"\nOffers found ({len(offers)}):")
        for o in offers:
            print(dict(zip(columns, o)))
            
        cursor.execute("SELECT id, product_name, price, original_price, offer_id FROM store_product WHERE offer_id IS NOT NULL;")
        linked_products = cursor.fetchall()
        print(f"\nProducts with linked offers ({len(linked_products)}):")
        for p in linked_products:
            print(p)
    else:
        print("store_offer table does not exist.")
        
    conn.close()
else:
    print("Database not found.")
