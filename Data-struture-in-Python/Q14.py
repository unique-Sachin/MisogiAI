# Corrected inventory dictionary
inventory = {
    "apples": {"price": 1.50, "quantity": 100},
    "bananas": {"price": 0.75, "quantity": 150},
    "oranges": {"price": 2.00, "quantity": 80}
}

# 1. Add a New Product
def add_product(name, price, quantity):
    inventory[name] = {"price": price, "quantity": quantity}
    print(f"Added product: {name}")

add_product("grapes", 2.50, 60)

# 2. Update Product Price
inventory["bananas"]["price"] = 0.85
print("Updated price of bananas.")

# 3. Sell 25 Apples
if inventory["apples"]["quantity"] >= 25:
    inventory["apples"]["quantity"] -= 25
    print("Sold 25 apples.")
else:
    print("Not enough apples in stock to sell 25.")

# 4. Calculate Total Inventory Value
total_value = sum(prod["price"] * prod["quantity"] for prod in inventory.values())
print(f"Total inventory value: ${total_value:.2f}")

# 5. Find Low Stock Products
low_stock = [name for name, prod in inventory.items() if prod["quantity"] < 100]
print(f"Low stock products (quantity < 100): {low_stock}")
