# Restaurant Food Menu & Order Management API

A fully functional Restaurant Food Menu and Order Management API built with FastAPI and Pydantic, featuring comprehensive validations, computed properties, and in-memory database storage.

## Features

### 🍕 Menu Management System
- **Auto-generated ID**: Primary key with auto-increment logic
- **Name validation**: Only letters and spaces (3-100 characters)
- **Description**: 10-500 characters
- **Category**: Enum-based categories (appetizer, main_course, dessert, beverage, salad)
- **Price**: Decimal with validation ($1.00 - $100.00)
- **Availability status**: Boolean flag
- **Preparation time**: 1-120 minutes
- **Ingredients**: List with minimum 1 item
- **Calories**: Optional positive integer
- **Dietary flags**: Vegetarian and spicy status

### 📦 Order Management System (NEW!)
- **Order Creation**: Nested customer + order items
- **Customer Validation**: Name (2-50 chars), 10-digit phone, optional address
- **Order Items**: Menu item ID, name, quantity (1-10), unit price
- **Status Management**: PENDING → CONFIRMED → READY → DELIVERED
- **Computed Properties**: Item totals and order totals
- **Status Transition Validation**: Prevents invalid status changes

### 🔍 Custom Validations
**Menu System:**
1. **Name validation**: No digits or special characters allowed
2. **Category rules**: 
   - Desserts and beverages cannot be spicy
   - Beverages must have prep time ≤ 10 minutes
3. **Dietary rules**: Vegetarian items (if calories provided) must have < 800 calories

**Order System:**
1. **Phone validation**: Must be exactly 10 digits
2. **Quantity limits**: 1-10 items per order item
3. **Item validation**: Menu item ID must be positive
4. **Order requirements**: Must have at least one item
5. **Status transitions**: Enforced workflow progression

### 📊 Computed Properties
**Menu Items:**
- **Price category**: "Budget" (<$10), "Mid-range" ($10-$25), "Premium" (>$25)
- **Dietary info**: Dynamic tags like ["Vegetarian", "Spicy", "Low Calorie"]

**Orders:**
- **Item totals**: quantity × unit_price for each item
- **Order total**: Sum of all item totals
- **Automatic timestamps**: Order creation time

## 🚀 Quick Start

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the server:
```bash
python restaurant_menu_api.py
```

3. Open your browser to:
- API Documentation: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc

### Test Order Management

Run the order system test cases:
```bash
python test_order_validations.py
```

Run the complete order management demo:
```bash
python demo_order_management.py
```

## 📡 API Endpoints

### Menu Management
- `GET /menu` - Get all menu items
- `GET /menu/{item_id}` - Get item by ID
- `POST /menu` - Create new menu item
- `PUT /menu/{item_id}` - Update existing item
- `DELETE /menu/{item_id}` - Delete item
- `GET /menu/category/{category}` - Filter by category
- `GET /menu/stats/summary` - Get menu statistics

### Order Management (NEW!)
- `POST /orders` - Create new order with customer and items
- `GET /orders` - Get all orders (summary view)
- `GET /orders/{order_id}` - Get specific order details
- `PUT /orders/{order_id}/status` - Update order status
- `GET /orders/stats/summary` - Get order statistics

## 📝 Sample Data

The API comes pre-loaded with 5 sample items:

1. **Margherita Pizza** (Main Course) - $12.99
2. **Spicy Chicken Wings** (Appetizer) - $8.99
3. **Caesar Salad** (Salad) - $7.50
4. **Chocolate Lava Cake** (Dessert) - $6.99
5. **Fresh Orange Juice** (Beverage) - $4.50

## 🧪 Test Cases Included

### Menu System Tests (`test_validations.py`)
1. ✅ **Valid creation**: Margherita Pizza with proper data
2. ❌ **Invalid price**: $0.50 (below minimum)
3. ❌ **Invalid category rule**: Spicy beverage (not allowed)
4. ❌ **Missing ingredients**: Empty ingredients list
5. ❌ **Invalid name**: "Pizza123!" (contains numbers/symbols)
6. ❌ **Beverage prep time**: >10 minutes (too long)
7. ❌ **High-calorie vegetarian**: ≥800 calories (exceeds limit)

### Order System Tests (`test_order_validations.py`)
1. ✅ **Valid order**: Create order with 2 items
2. ❌ **Empty items**: Order with empty items list
3. ❌ **Invalid phone**: Customer phone not 10 digits
4. ❌ **Large quantity**: quantity = 15 (exceeds limit)
5. ✅ **Status update**: Change from PENDING to CONFIRMED
6. ❌ **Invalid menu item ID**: Negative ID
7. ❌ **Invalid unit price**: Negative price

## 📋 Example API Usage

### Create a New Order
```bash
curl -X POST "http://localhost:8000/orders" \
     -H "Content-Type: application/json" \
     -d '{
       "customer": {
         "name": "Alice Smith",
         "phone": "5551234567",
         "address": "123 Oak Street, Springfield"
       },
       "items": [
         {
           "menu_item_id": 1,
           "menu_item_name": "Margherita Pizza",
           "quantity": 1,
           "unit_price": "15.99"
         },
         {
           "menu_item_id": 2,
           "menu_item_name": "Spicy Chicken Wings",
           "quantity": 2,
           "unit_price": "12.50"
         }
       ]
     }'
```

### Update Order Status
```bash
curl -X PUT "http://localhost:8000/orders/1/status" \
     -H "Content-Type: application/json" \
     -d '{"status": "confirmed"}'
```

### Get All Orders
```bash
curl "http://localhost:8000/orders"
```

## 🏗️ Project Structure

```
├── restaurant_menu_api.py       # Main API application with menu & order management
├── test_validations.py          # Menu validation test cases
├── test_order_validations.py    # Order validation test cases
├── demo_api.py                  # Menu system demo script
├── demo_order_management.py     # Order system demo script
├── requirements.txt             # Python dependencies
└── README.md                   # This file
```

## 🔧 Technical Implementation

### In-Memory Databases
- **Menu Database**: `menu_db: Dict[int, FoodItem] = {}`
- **Orders Database**: `orders_db: Dict[int, Order] = {}`
- Auto-increment ID management with separate counters
- Thread-safe for single-process deployment

### Pydantic Models
**Menu System:**
- `FoodItem`: Main model with all validations and computed properties
- `FoodItemCreate`: Input model for creating items
- `FoodItemUpdate`: Input model for partial updates

**Order System:**
- `Order`: Complete order with customer and items
- `OrderItem`: Individual item within an order
- `Customer`: Customer information with phone validation
- `OrderCreate`: Input model for creating orders
- `OrderStatusUpdate`: Input model for status updates
- `OrderResponse`: Full order response
- `OrderSummaryResponse`: Summary for listings

### Custom Validators
- `@validator` decorators for field-level validation
- `@root_validator` for cross-field business rules
- Property methods for computed values

## 🌟 Key Features Demonstrated

1. **Complex Pydantic Validations**: Multiple validation layers with custom rules
2. **Computed Properties**: Dynamic values calculated from base fields
3. **Enum Usage**: Type-safe category system
4. **Decimal Handling**: Proper price handling with precision
5. **Error Handling**: Comprehensive HTTP error responses
6. **Auto Documentation**: FastAPI auto-generates interactive docs

## 🚦 Validation Examples

The API enforces strict business rules:

```python
# ❌ This will fail - spicy beverage not allowed
{
  "name": "Spicy Coffee",
  "category": "beverage",
  "is_spicy": true  # ValidationError!
}

# ❌ This will fail - beverage prep time too long
{
  "name": "Complex Smoothie", 
  "category": "beverage",
  "preparation_time": 15  # ValidationError! Max 10 for beverages
}

# ✅ This will succeed
{
  "name": "Fresh Lemonade",
  "category": "beverage", 
  "preparation_time": 5,
  "is_spicy": false
}
```

## 📈 Computed Properties in Action

Each item automatically calculates:

```json
{
  "id": 1,
  "name": "Margherita Pizza",
  "price": 12.99,
  "price_category": "Mid-range",  // Computed
  "is_vegetarian": true,
  "is_spicy": false,
  "calories": 650,
  "dietary_info": ["Vegetarian"]  // Computed
}
```

This implementation provides a robust, production-ready foundation for a restaurant menu management system with comprehensive validation and business rule enforcement.
