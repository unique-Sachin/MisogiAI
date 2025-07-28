# Given data
products = ["Laptop", "Mouse", "Keyboard", "Monitor"]
prices = [1999.99, 25.50, 75.00, 299.99]
quantities = [15, 20, 15, 8]

product_price_pairs = list(zip(products, prices))
print("Product-Price pairs:", product_price_pairs)

product_total_values = [(product, price * quantity) for product, price, quantity in zip(products, prices, quantities)]
print("Total value for each product:", product_total_values)

product_catalog = {product: {"price": price, "quantity": quantity} for product, price, quantity in zip(products, prices, quantities)}
print("Product catalog:", product_catalog)

low_stock_products = [product for product, quantity in zip(products, quantities) if quantity < 10]
print("Low stock products:", low_stock_products)
