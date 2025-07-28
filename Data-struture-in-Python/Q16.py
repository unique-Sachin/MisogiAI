sales_data = [
    ("Q1", [("Jan", 1000), ("Feb", 1200), ("Mar", 1100)]),
    ("Q2", [("Apr", 1300), ("May", 1250), ("Jun", 1400)]),
    ("Q3", [("Jul", 1350), ("Aug", 1450), ("Sep", 1300)])
]

# 1. Calculate Total Sales per Quarter
print("Total Sales Per Quarter:")
for quarter, monthly_data in sales_data:
    total = sum(sale for month, sale in monthly_data)
    print(f"{quarter}: {total}")
print()

# 2. Find the Month with Highest Sales
all_months = [(month, sale) for _, data in sales_data for (month, sale) in data]
highest_month = max(all_months, key=lambda x: x[1])
print(f"Month with Highest Sales: {highest_month[0]} ({highest_month[1]})")
print()

# 3. Create a Flat List of Monthly Sales
flat_sales = [(month, sale) for _, data in sales_data for (month, sale) in data]
print("Flat List of Monthly Sales:")
print(flat_sales)
print()

# 4. Use Unpacking in Loops
print("Detailed Monthly Sales with Unpacking:")
for quarter, monthly_data in sales_data:
    for month, sale in monthly_data:
        print(f"Quarter: {quarter}, Month: {month}, Sales: {sale}")