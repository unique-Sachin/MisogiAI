from collections import defaultdict

class Product:
    _total_products = 0
    _category_sales = defaultdict(int)  # category -> quantity sold

    def __init__(self, product_id, name, price, category, stock_quantity):
        if price < 0 or stock_quantity < 0:
            raise ValueError("Price and stock must be non-negative.")
        self.product_id = product_id
        self.name = name
        self.price = price
        self.category = category
        self.stock_quantity = stock_quantity
        Product._total_products += 1

    def get_product_info(self):
        return f"{self.name} (${self.price}) - {self.category}, Stock: {self.stock_quantity}"

    def reduce_stock(self, quantity):
        if quantity > self.stock_quantity:
            raise ValueError("Insufficient stock.")
        self.stock_quantity -= quantity
        Product._category_sales[self.category] += quantity

    @classmethod
    def get_total_products(cls):
        return cls._total_products

    @classmethod
    def get_most_popular_category(cls):
        if not cls._category_sales:
            return None
        return max(cls._category_sales.items(), key=lambda x: x[1])[0]


class Customer:
    _total_revenue = 0.0

    def __init__(self, customer_id, name, email, membership_type="regular"):
        self.customer_id = customer_id
        self.name = name
        self.email = email
        self.membership_type = membership_type.lower()

    def __str__(self):
        return f"{self.name} ({self.membership_type})"

    def get_discount_rate(self):
        return {"regular": 0, "premium": 10, "vip": 20}.get(self.membership_type, 0)

    def add_revenue(self, amount):
        Customer._total_revenue += amount

    @classmethod
    def get_total_revenue(cls):
        return round(cls._total_revenue, 2)


class ShoppingCart:
    def __init__(self, customer):
        self.customer = customer
        self.items = {}  # product_id -> (Product, quantity)

    def add_item(self, product, quantity):
        if quantity <= 0:
            raise ValueError("Quantity must be positive.")
        if product.product_id in self.items:
            self.items[product.product_id][1] += quantity
        else:
            self.items[product.product_id] = [product, quantity]

    def remove_item(self, product_id):
        if product_id in self.items:
            del self.items[product_id]

    def clear_cart(self):
        self.items.clear()

    def get_total_items(self):
        return sum(quantity for _, quantity in self.items.values())

    def get_subtotal(self):
        return round(sum(product.price * quantity for product, quantity in self.items.values()), 2)

    def calculate_total(self):
        subtotal = self.get_subtotal()
        discount_rate = self.customer.get_discount_rate()
        discount_amount = subtotal * (discount_rate / 100)
        return round(subtotal - discount_amount, 2)

    def place_order(self):
        try:
            # Check and reduce inventory
            for product, quantity in self.items.values():
                if quantity > product.stock_quantity:
                    raise ValueError(f"Insufficient stock for {product.name}")
            for product, quantity in self.items.values():
                product.reduce_stock(quantity)

            # Record revenue
            total = self.calculate_total()
            self.customer.add_revenue(total)

            # Clear cart after successful order
            self.clear_cart()
            return f"Order placed successfully. Total: ${total}"
        except Exception as e:
            return f"Order failed: {str(e)}"

    def get_cart_items(self):
        return {pid: {"name": prod.name, "quantity": qty} for pid, (prod, qty) in self.items.items()}
    


# Test Case 1: Creating products with different categories
laptop = Product("P001", "Gaming Laptop", 1299.99, "Electronics", 10)
book = Product("P002", "Python Programming", 49.99, "Books", 25)
shirt = Product("P003", "Cotton T-Shirt", 19.99, "Clothing", 50)
print(f"product info: {laptop.get_product_info()}")
print(f"Total products in system: {Product.get_total_products()}")

# Test Case 2: Creating customer and shopping cart
customer = Customer("C001", "John Doe", "john@email.com", "premium")
cart = ShoppingCart(customer)
print(f"Customer: {customer}")
print(f"Customer discount: {customer.get_discount_rate()}%")

# Test Case 3: Adding items to cart
cart.add_item(laptop, 1)
cart.add_item(book, 2)
cart.add_item(shirt, 3)
print(f"Cart total items: {cart.get_total_items()}")
print(f"Cart subtotal: ${cart.get_subtotal()}")

# Test Case 4: Applying discounts and calculating final price
final_total = cart.calculate_total()
print(f"Final total (with {customer.get_discount_rate()}% discount): ${final_total}")

# Test Case 5: Inventory management
print(f"Laptop stock before order: {laptop.stock_quantity}")
order_result = cart.place_order()
print(f"Order result: {order_result}")
print(f"Laptop stock after order: {laptop.stock_quantity}")

# Test Case 6: Class methods for business analytics
popular_category = Product.get_most_popular_category()
print(f"Most popular category: {popular_category}")
total_revenue = Customer.get_total_revenue()
print(f"Total revenue: ${total_revenue}")

# Test Case 7: Cart operations
cart.remove_item("P002")  # Remove book (should already be cleared if order was successful)
print(f"Items after removal: {cart.get_cart_items()}")
cart.clear_cart()
print(f"Items after clearing: {cart.get_total_items()}")