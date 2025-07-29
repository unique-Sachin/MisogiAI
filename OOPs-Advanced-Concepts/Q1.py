class Product:
    def __init__(self, name, base_price, discount_percent, stock_quantity, category):
        self.name = name
        self.base_price = base_price
        self.discount_percent = discount_percent
        self.stock_quantity = stock_quantity
        self.category = category

    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, value):
        if not isinstance(value, str):
            raise ValueError("Name must be a string.")
        if not (3 <= len(value) <= 50):
            raise ValueError("Name must be 3-50 characters.")
        if not all(c.isalnum() or c in ' -' for c in value):
            raise ValueError("Name must contain only letters, numbers, spaces, and hyphens.")
        self._name = value

    @property
    def base_price(self):
        return self._base_price

    @base_price.setter
    def base_price(self, value):
        if not isinstance(value, (int, float)):
            raise ValueError("Base price must be a number.")
        if value <= 0:
            raise ValueError("Base price must be positive.")
        if value > 50000:
            raise ValueError("Base price must not exceed $50,000.")
        self._base_price = value

    @property
    def discount_percent(self):
        return self._discount_percent

    @discount_percent.setter
    def discount_percent(self, value):
        if not isinstance(value, (int, float)):
            raise ValueError("Discount percent must be a number.")
        if not (0 <= value <= 75):
            raise ValueError("Discount percent must be between 0 and 75.")
        self._discount_percent = round(value, 2)

    @property
    def stock_quantity(self):
        return self._stock_quantity

    @stock_quantity.setter
    def stock_quantity(self, value):
        if not isinstance(value, int):
            raise ValueError("Stock quantity must be an integer.")
        if value < 0:
            raise ValueError("Stock quantity must be non-negative.")
        if value > 10000:
            raise ValueError("Stock quantity must not exceed 10,000 units.")
        self._stock_quantity = value

    @property
    def category(self):
        return self._category

    @category.setter
    def category(self, value):
        if not isinstance(value, str):
            raise ValueError("Category must be a string.")
        valid_categories = ['Electronics', 'Clothing', 'Books', 'Home', 'Sports']
        if value not in valid_categories:
            raise ValueError(f"Category must be one of: {valid_categories}")
        self._category = value

    @property
    def final_price(self):
        discount_amount = (self._base_price * self._discount_percent) / 100
        return round(self._base_price - discount_amount, 2)
    
    @property
    def availability_status(self):
        if self._stock_quantity > 0 and self._stock_quantity >= 10:
            return "In Stock"
        elif self._stock_quantity < 10 and self._stock_quantity > 0:
            return "Low Stock"
        else:
            return "Out of Stock"
        
    @property
    def savings_amount(self):
        return round((self._base_price * self._discount_percent) / 100, 2)
    
    @property
    def product_summary(self):
        return f"Product: {self._name}, Base Price: {self._base_price}, Final Price: {self.final_price}, Availability: {self.availability_status}, Category: {self._category}"



# Test Case 1: Valid product creation and automatic calculations
product = Product("Gaming Laptop", 1299.99, 15.5, 25, "Electronics")
assert product.name == "Gaming Laptop"
assert product.base_price == 1299.99
assert product.discount_percent == 15.5
assert abs(product.final_price - 1098.49) < 0.01
assert abs(product.savings_amount - 201.49) < 0.01
assert product.availability_status == "In Stock"

# Test Case 2: Property setters with automatic recalculation
product.discount_percent = 20.567  # Should round to 20.57
assert product.discount_percent == 20.57
assert abs(product.final_price - 1032.58) < 0.01
product.stock_quantity = 5
assert product.availability_status == "Low Stock"

# Test Case 3: Validation edge cases
try:
    product.name = "AB"  # Too short
    assert False, "Should raise ValueError"
except ValueError as e:
    assert "3-50 characters" in str(e)

try:
    product.base_price = -100  # Negative price
    assert False, "Should raise ValueError"
except ValueError:
    pass

try:
    product.category = "InvalidCategory"
    assert False, "Should raise ValueError"
except ValueError:
    pass

# Test Case 4: Product summary formatting
assert "Gaming Laptop" in product.product_summary
assert "1299.99" in product.product_summary
assert "Low Stock" in product.product_summary
