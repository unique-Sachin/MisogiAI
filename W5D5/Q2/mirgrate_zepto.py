import pandas as pd
import sqlite3

# === Step 1: Load and preprocess the data ===
df = pd.read_csv("dataset/zepto_v2.csv", encoding="ISO-8859-1")

# Clean boolean column
df['outOfStock'] = df['outOfStock'].astype(str).str.upper().map({'FALSE': 0, 'TRUE': 1})

# === Step 2: Connect to SQLite and create schema ===
conn = sqlite3.connect("zepto.db")
cursor = conn.cursor()

# Create Category table
cursor.execute("""
CREATE TABLE IF NOT EXISTS Category (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
)
""")

# Create Product table
cursor.execute("""
CREATE TABLE IF NOT EXISTS Product (
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    mrp INTEGER,
    discount_percent INTEGER,
    discounted_price INTEGER,
    weight_in_gms INTEGER,
    category_id INTEGER,
    FOREIGN KEY (category_id) REFERENCES Category(category_id)
)
""")

# Create Inventory table
cursor.execute("""
CREATE TABLE IF NOT EXISTS Inventory (
    inventory_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER,
    available_quantity INTEGER,
    quantity INTEGER,
    out_of_stock BOOLEAN,
    FOREIGN KEY (product_id) REFERENCES Product(product_id)
)
""")

conn.commit()

# === Step 3: Insert unique categories ===
unique_categories = df['Category'].dropna().unique()
for cat in unique_categories:
    cursor.execute("INSERT OR IGNORE INTO Category (name) VALUES (?)", (cat,))
conn.commit()

# Create a mapping from category name to category_id
cursor.execute("SELECT * FROM Category")
category_map = {name: cid for cid, name in cursor.fetchall()}

# === Step 4: Insert products and inventory ===
for _, row in df.iterrows():
    cat_id = category_map.get(row['Category'])
    if cat_id is None:
        continue  # skip if no category matched (unlikely)

    # Insert into Product
    cursor.execute("""
        INSERT INTO Product (name, mrp, discount_percent, discounted_price, weight_in_gms, category_id)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        row['name'],
        row['mrp'],
        row['discountPercent'],
        row['discountedSellingPrice'],
        row['weightInGms'],
        cat_id
    ))
    product_id = cursor.lastrowid

    # Insert into Inventory
    cursor.execute("""
        INSERT INTO Inventory (product_id, available_quantity, quantity, out_of_stock)
        VALUES (?, ?, ?, ?)
    """, (
        product_id,
        row['availableQuantity'],
        row['quantity'],
        row['outOfStock']
    ))

conn.commit()
conn.close()

print("✅ Data successfully normalized into multiple tables.")