import pandas as pd
import sqlite3

# === Load CSV ===
df = pd.read_csv("dataset/blinkit.csv")
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

# === Connect to DB ===
conn = sqlite3.connect("blinkit.db")
cursor = conn.cursor()

# === Create Tables ===
cursor.execute("""
CREATE TABLE IF NOT EXISTS Category (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Brand (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Product (
    id INTEGER PRIMARY KEY,
    name TEXT,
    category_id INTEGER,
    brand_id INTEGER,
    price REAL,
    mrp REAL,
    margin_percentage REAL,
    shelf_life_days INTEGER,
    min_stock_level INTEGER,
    max_stock_level INTEGER,
    FOREIGN KEY (category_id) REFERENCES Category(id),
    FOREIGN KEY (brand_id) REFERENCES Brand(id)
)
""")

# === Insert Data ===
for _, row in df.iterrows():
    # Insert Category
    cursor.execute("INSERT OR IGNORE INTO Category (name) VALUES (?)", (row['category'],))
    cursor.execute("SELECT id FROM Category WHERE name = ?", (row['category'],))
    category_id = cursor.fetchone()[0]

    # Insert Brand
    cursor.execute("INSERT OR IGNORE INTO Brand (name) VALUES (?)", (row['brand'],))
    cursor.execute("SELECT id FROM Brand WHERE name = ?", (row['brand'],))
    brand_id = cursor.fetchone()[0]

    # Insert Product
    cursor.execute("""
        INSERT OR REPLACE INTO Product (
            id, name, category_id, brand_id, price, mrp, margin_percentage,
            shelf_life_days, min_stock_level, max_stock_level
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        row['product_id'],
        row['product_name'],
        category_id,
        brand_id,
        row['price'],
        row['mrp'],
        row['margin_percentage'],
        row['shelf_life_days'],
        row['min_stock_level'],
        row['max_stock_level']
    ))

conn.commit()
conn.close()
print("✅ blinkit.db created with Product, Category, Brand tables.")