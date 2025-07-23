# Constants
TAX_RATE = 0.085

# Input for item 1
price1 = float(input("Enter price of item 1: "))
qty1 = int(input("Enter quantity of item 1: "))

# Input for item 2
price2 = float(input("Enter price of item 2: "))
qty2 = int(input("Enter quantity of item 2: "))

# Input for item 3
price3 = float(input("Enter price of item 3: "))
qty3 = int(input("Enter quantity of item 3: "))

# Calculations
total1 = price1 * qty1
total2 = price2 * qty2
total3 = price3 * qty3
subtotal = total1 + total2 + total3
tax = round(subtotal * TAX_RATE, 2)
total = round(subtotal + tax, 2)

# Output
print()
print(f"Item 1: {price1} x {qty1} = {int(total1)}")
print(f"Item 2: {price2} x {qty2} = {int(total2)}")
print(f"Item 3: {price3} x {qty3} = {int(total3)}")
print(f"Subtotal: {int(subtotal)}")
print(f"Tax (8.5%): {tax}")
print(f"Total: {total}")