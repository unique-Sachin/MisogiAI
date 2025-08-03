"""
FastAPI Restaurant Food Menu Management API with Pydantic Validations
A fully functional restaurant menu management system with custom validations
and computed properties using in-memory dictionary storage.
"""

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field, field_validator, model_validator
from enum import Enum
from typing import List, Optional, Dict, Any
from decimal import Decimal
import re
from datetime import datetime

# Enum for food categories
class FoodCategory(str, Enum):
    APPETIZER = "appetizer"
    MAIN_COURSE = "main_course"
    DESSERT = "dessert"
    BEVERAGE = "beverage"
    SALAD = "salad"

# Enum for order status
class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    READY = "ready"
    DELIVERED = "delivered"

# Pydantic model for FoodItem with custom validations
class FoodItem(BaseModel):
    id: Optional[int] = None  # Auto-generated
    name: str = Field(..., min_length=3, max_length=100, description="Food item name")
    description: str = Field(..., min_length=10, max_length=500, description="Food item description")
    category: FoodCategory = Field(..., description="Food category")
    price: Decimal = Field(..., ge=1.00, le=100.00, description="Price in USD")
    is_available: bool = Field(default=True, description="Availability status")
    preparation_time: int = Field(..., ge=1, le=120, description="Preparation time in minutes")
    ingredients: List[str] = Field(..., description="List of ingredients")
    calories: Optional[int] = Field(None, gt=0, description="Calories count")
    is_vegetarian: bool = Field(default=False, description="Vegetarian status")
    is_spicy: bool = Field(default=False, description="Spicy status")

    class Config:
        # Enable the use of Decimal for JSON serialization
        json_encoders = {
            Decimal: lambda v: float(v)
        }

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        """Validate that name contains only letters and spaces"""
        if not re.match(r'^[a-zA-Z\s]+$', v):
            raise ValueError('Name must contain only letters and spaces')
        return v.strip()

    @field_validator('ingredients')
    @classmethod
    def validate_ingredients(cls, v):
        """Validate ingredients list"""
        if not v:
            raise ValueError('At least one ingredient is required')
        # Clean up ingredients (strip whitespace)
        return [ingredient.strip() for ingredient in v if ingredient.strip()]

    @model_validator(mode='after')
    def validate_food_rules(self):
        """Custom validation rules based on category and properties"""
        category = self.category
        is_spicy = self.is_spicy
        preparation_time = self.preparation_time
        is_vegetarian = self.is_vegetarian
        calories = self.calories

        # Rule 1: Desserts and beverages cannot be spicy
        if category in [FoodCategory.DESSERT, FoodCategory.BEVERAGE] and is_spicy:
            raise ValueError(f'{category.value} items cannot be spicy')

        # Rule 2: Beverages must have prep time ≤ 10 minutes
        if category == FoodCategory.BEVERAGE and preparation_time > 10:
            raise ValueError('Beverages must have preparation time of 10 minutes or less')

        # Rule 3: Vegetarian items (if calories provided) must have calories < 800
        if is_vegetarian and calories is not None and calories >= 800:
            raise ValueError('Vegetarian items must have less than 800 calories')

        return self

    @property
    def price_category(self) -> str:
        """Computed property for price category"""
        if self.price < 10:
            return "Budget"
        elif self.price <= 25:
            return "Mid-range"
        else:
            return "Premium"

    @property
    def dietary_info(self) -> List[str]:
        """Computed property for dietary information tags"""
        tags = []
        if self.is_vegetarian:
            tags.append("Vegetarian")
        if self.is_spicy:
            tags.append("Spicy")
        if self.calories and self.calories < 300:
            tags.append("Low Calorie")
        return tags

    def dict(self, *args, **kwargs) -> Dict[str, Any]:
        """Override dict method to include computed properties"""
        data = super().dict(*args, **kwargs)
        data['price_category'] = self.price_category
        data['dietary_info'] = self.dietary_info
        return data

# Request models for API
class FoodItemCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: str = Field(..., min_length=10, max_length=500)
    category: FoodCategory
    price: Decimal = Field(..., ge=1.00, le=100.00)
    is_available: bool = Field(default=True)
    preparation_time: int = Field(..., ge=1, le=120)
    ingredients: List[str] = Field(...)
    calories: Optional[int] = Field(None, gt=0)
    is_vegetarian: bool = Field(default=False)
    is_spicy: bool = Field(default=False)

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not re.match(r'^[a-zA-Z\s]+$', v):
            raise ValueError('Name must contain only letters and spaces')
        return v.strip()

    @field_validator('ingredients')
    @classmethod
    def validate_ingredients(cls, v):
        if not v:
            raise ValueError('At least one ingredient is required')
        return [ingredient.strip() for ingredient in v if ingredient.strip()]

    @model_validator(mode='after')
    def validate_food_rules(self):
        category = self.category
        is_spicy = self.is_spicy
        preparation_time = self.preparation_time
        is_vegetarian = self.is_vegetarian
        calories = self.calories

        if category in [FoodCategory.DESSERT, FoodCategory.BEVERAGE] and is_spicy:
            raise ValueError(f'{category.value} items cannot be spicy')

        if category == FoodCategory.BEVERAGE and preparation_time > 10:
            raise ValueError('Beverages must have preparation time of 10 minutes or less')

        if is_vegetarian and calories is not None and calories >= 800:
            raise ValueError('Vegetarian items must have less than 800 calories')

        return self

class FoodItemUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, min_length=10, max_length=500)
    category: Optional[FoodCategory] = None
    price: Optional[Decimal] = Field(None, ge=1.00, le=100.00)
    is_available: Optional[bool] = None
    preparation_time: Optional[int] = Field(None, ge=1, le=120)
    ingredients: Optional[List[str]] = Field(None)
    calories: Optional[int] = Field(None, gt=0)
    is_vegetarian: Optional[bool] = None
    is_spicy: Optional[bool] = None

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if v is not None and not re.match(r'^[a-zA-Z\s]+$', v):
            raise ValueError('Name must contain only letters and spaces')
        return v.strip() if v else v

    @field_validator('ingredients')
    @classmethod
    def validate_ingredients(cls, v):
        if v is not None:
            if not v:
                raise ValueError('At least one ingredient is required')
            return [ingredient.strip() for ingredient in v if ingredient.strip()]
        return v

# ===== ORDER MANAGEMENT MODELS =====

class OrderItem(BaseModel):
    """Individual item within an order"""
    menu_item_id: int = Field(..., gt=0, description="Menu item ID (must be positive)")
    menu_item_name: str = Field(..., min_length=1, max_length=100, description="Name of the menu item")
    quantity: int = Field(..., ge=1, le=10, description="Quantity (1-10)")
    unit_price: Decimal = Field(..., gt=0, description="Unit price (must be positive)")

    @property
    def item_total(self) -> Decimal:
        """Computed property: total cost for this item"""
        return self.quantity * self.unit_price

    def dict(self, *args, **kwargs) -> Dict[str, Any]:
        """Override dict method to include computed properties"""
        data = super().model_dump(*args, **kwargs)
        data['item_total'] = float(self.item_total)
        return data

class Customer(BaseModel):
    """Customer information"""
    name: str = Field(..., min_length=2, max_length=50, description="Customer name")
    phone: str = Field(..., description="10-digit phone number")
    address: Optional[str] = Field(None, description="Customer address (optional but recommended)")

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        """Validate phone number format (10 digits)"""
        if not re.match(r'^\d{10}$', v):
            raise ValueError('Phone number must be exactly 10 digits')
        return v

class Order(BaseModel):
    """Complete order with customer and items"""
    id: Optional[int] = None  # Auto-generated
    customer: Customer = Field(..., description="Customer information")
    items: List[OrderItem] = Field(..., min_length=1, description="Order items (minimum 1)")
    status: OrderStatus = Field(default=OrderStatus.PENDING, description="Order status")
    created_at: Optional[datetime] = Field(default_factory=datetime.now, description="Order creation timestamp")

    @property
    def order_total(self) -> Decimal:
        """Computed property: total cost for the entire order"""
        return sum((item.item_total for item in self.items), Decimal('0'))

    def dict(self, *args, **kwargs) -> Dict[str, Any]:
        """Override dict method to include computed properties"""
        data = super().model_dump(*args, **kwargs)
        data['order_total'] = float(self.order_total)
        # Ensure items include their computed properties
        data['items'] = [item.dict() for item in self.items]
        return data

# Request/Response Models for Orders

class OrderItemCreate(BaseModel):
    """Model for creating order items"""
    menu_item_id: int = Field(..., gt=0)
    menu_item_name: str = Field(..., min_length=1, max_length=100)
    quantity: int = Field(..., ge=1, le=10)
    unit_price: Decimal = Field(..., gt=0)

class CustomerCreate(BaseModel):
    """Model for creating customer information"""
    name: str = Field(..., min_length=2, max_length=50)
    phone: str = Field(...)
    address: Optional[str] = Field(None)

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        if not re.match(r'^\d{10}$', v):
            raise ValueError('Phone number must be exactly 10 digits')
        return v

class OrderCreate(BaseModel):
    """Model for creating new orders"""
    customer: CustomerCreate = Field(...)
    items: List[OrderItemCreate] = Field(..., min_length=1)

    @field_validator('items')
    @classmethod
    def validate_items(cls, v):
        if not v:
            raise ValueError('Order must have at least one item')
        return v

class OrderStatusUpdate(BaseModel):
    """Model for updating order status"""
    status: OrderStatus = Field(..., description="New order status")

class OrderResponse(BaseModel):
    """Full order response with all details"""
    id: int
    customer: Customer
    items: List[Dict[str, Any]]
    status: OrderStatus
    created_at: datetime
    order_total: float

class OrderSummaryResponse(BaseModel):
    """Summary response for order listings"""
    id: int
    customer_name: str
    order_total: float
    status: OrderStatus
    created_at: datetime
    item_count: int

class ErrorResponse(BaseModel):
    """Error response model"""
    detail: str
    error_code: Optional[str] = None

# ===== IN-MEMORY DATABASES =====

# Menu database (existing)
menu_db: Dict[int, FoodItem] = {}
next_menu_id = 1

# Orders database (new)
orders_db: Dict[int, Order] = {}
next_order_id = 1

# Auto-increment ID logic for menu items
def get_next_menu_id() -> int:
    global next_menu_id
    current_id = next_menu_id
    next_menu_id += 1
    return current_id

# Auto-increment ID logic for orders
def get_next_order_id() -> int:
    global next_order_id
    current_id = next_order_id
    next_order_id += 1
    return current_id

# Initialize FastAPI app
app = FastAPI(
    title="Restaurant Menu Management API",
    description="A comprehensive food menu management system with Pydantic validations",
    version="1.0.0"
)

# Seed sample data
def seed_sample_data():
    """Populate the database with sample menu items"""
    sample_items = [
        {
            "name": "Margherita Pizza",
            "description": "Classic pizza with fresh tomatoes, mozzarella cheese, and basil leaves on a crispy crust",
            "category": FoodCategory.MAIN_COURSE,
            "price": Decimal("12.99"),
            "preparation_time": 15,
            "ingredients": ["Pizza dough", "Tomato sauce", "Mozzarella cheese", "Fresh basil", "Olive oil"],
            "calories": 650,
            "is_vegetarian": True,
            "is_spicy": False
        },
        {
            "name": "Spicy Chicken Wings",
            "description": "Crispy chicken wings tossed in our signature hot sauce with a side of blue cheese dip",
            "category": FoodCategory.APPETIZER,
            "price": Decimal("8.99"),
            "preparation_time": 20,
            "ingredients": ["Chicken wings", "Hot sauce", "Butter", "Garlic", "Blue cheese dip"],
            "calories": 450,
            "is_vegetarian": False,
            "is_spicy": True
        },
        {
            "name": "Caesar Salad",
            "description": "Fresh romaine lettuce with parmesan cheese, croutons, and classic Caesar dressing",
            "category": FoodCategory.SALAD,
            "price": Decimal("7.50"),
            "preparation_time": 8,
            "ingredients": ["Romaine lettuce", "Parmesan cheese", "Croutons", "Caesar dressing", "Lemon"],
            "calories": 280,
            "is_vegetarian": True,
            "is_spicy": False
        },
        {
            "name": "Chocolate Lava Cake",
            "description": "Warm chocolate cake with a molten chocolate center served with vanilla ice cream",
            "category": FoodCategory.DESSERT,
            "price": Decimal("6.99"),
            "preparation_time": 12,
            "ingredients": ["Dark chocolate", "Butter", "Eggs", "Sugar", "Flour", "Vanilla ice cream"],
            "calories": 520,
            "is_vegetarian": True,
            "is_spicy": False
        },
        {
            "name": "Fresh Orange Juice",
            "description": "Freshly squeezed orange juice served chilled with a slice of orange",
            "category": FoodCategory.BEVERAGE,
            "price": Decimal("4.50"),
            "preparation_time": 5,
            "ingredients": ["Fresh oranges", "Ice"],
            "calories": 110,
            "is_vegetarian": True,
            "is_spicy": False
        }
    ]
    
    global menu_db, next_menu_id
    for item_data in sample_items:
        item_id = get_next_menu_id()
        food_item = FoodItem(id=item_id, **item_data)
        menu_db[item_id] = food_item

# Seed data on startup
seed_sample_data()

# API Endpoints

@app.get("/")
def root():
    """Root endpoint with API information"""
    return {
        "message": "Restaurant Menu Management API",
        "version": "1.0.0",
        "endpoints": {
            "menu": "/menu",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }

@app.get("/menu", response_model=List[Dict[str, Any]])
def get_all_menu_items():
    """Get all menu items with computed properties"""
    return [item.dict() for item in menu_db.values()]

@app.get("/menu/{item_id}", response_model=Dict[str, Any])
def get_menu_item(item_id: int):
    """Get a specific menu item by ID"""
    if item_id not in menu_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Menu item with ID {item_id} not found"
        )
    return menu_db[item_id].dict()

@app.post("/menu", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
def create_menu_item(item: FoodItemCreate):
    """Create a new menu item with auto-generated ID"""
    try:
        item_id = get_next_menu_id()
        food_item = FoodItem(id=item_id, **item.model_dump())
        menu_db[item_id] = food_item
        return food_item.dict()
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )

@app.put("/menu/{item_id}", response_model=Dict[str, Any])
def update_menu_item(item_id: int, item: FoodItemUpdate):
    """Update an existing menu item"""
    if item_id not in menu_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Menu item with ID {item_id} not found"
        )
    
    try:
        # Get current item
        current_item = menu_db[item_id]
        
        # Update only provided fields
        update_data = item.model_dump(exclude_unset=True)
        current_data = current_item.dict()
        current_data.update(update_data)
        
        # Remove computed properties from update data
        current_data.pop('price_category', None)
        current_data.pop('dietary_info', None)
        
        # Create updated item
        updated_item = FoodItem(**current_data)
        menu_db[item_id] = updated_item
        
        return updated_item.dict()
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )

@app.delete("/menu/{item_id}")
def delete_menu_item(item_id: int):
    """Delete a menu item"""
    if item_id not in menu_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Menu item with ID {item_id} not found"
        )
    
    deleted_item = menu_db.pop(item_id)
    return {
        "message": f"Menu item '{deleted_item.name}' deleted successfully",
        "deleted_item_id": item_id
    }

@app.get("/menu/category/{category}", response_model=List[Dict[str, Any]])
def get_menu_items_by_category(category: FoodCategory):
    """Get all menu items filtered by category"""
    filtered_items = [
        item.dict() for item in menu_db.values() 
        if item.category == category
    ]
    
    if not filtered_items:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No menu items found for category: {category}"
        )
    
    return filtered_items

# Additional utility endpoints

@app.get("/menu/stats/summary")
def get_menu_summary():
    """Get menu statistics and summary"""
    if not menu_db:
        return {"message": "No menu items available"}
    
    items = list(menu_db.values())
    
    # Calculate statistics
    total_items = len(items)
    available_items = sum(1 for item in items if item.is_available)
    vegetarian_items = sum(1 for item in items if item.is_vegetarian)
    spicy_items = sum(1 for item in items if item.is_spicy)
    
    # Price statistics
    prices = [float(item.price) for item in items]
    avg_price = sum(prices) / len(prices)
    min_price = min(prices)
    max_price = max(prices)
    
    # Category breakdown
    category_counts = {}
    for item in items:
        category_counts[item.category.value] = category_counts.get(item.category.value, 0) + 1
    
    return {
        "total_items": total_items,
        "available_items": available_items,
        "vegetarian_items": vegetarian_items,
        "spicy_items": spicy_items,
        "price_stats": {
            "average": round(avg_price, 2),
            "minimum": min_price,
            "maximum": max_price
        },
        "category_breakdown": category_counts
    }

# ===== ORDER MANAGEMENT ENDPOINTS =====

@app.post("/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(order_data: OrderCreate):
    """Create a new order with customer and items"""
    try:
        # Convert input data to order items and customer
        order_items = [
            OrderItem(**item.model_dump()) for item in order_data.items
        ]
        customer = Customer(**order_data.customer.model_dump())
        
        # Create the order
        order_id = get_next_order_id()
        new_order = Order(
            id=order_id,
            customer=customer,
            items=order_items
        )
        
        # Store in database
        orders_db[order_id] = new_order
        
        # Return response
        return OrderResponse(
            id=new_order.id,  # type: ignore
            customer=new_order.customer,
            items=[item.dict() for item in new_order.items],
            status=new_order.status,
            created_at=new_order.created_at,  # type: ignore
            order_total=float(new_order.order_total)
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )

@app.get("/orders", response_model=List[OrderSummaryResponse])
def get_all_orders():
    """Get list of all orders with summary information"""
    if not orders_db:
        return []
    
    summaries = []
    for order in orders_db.values():
        summaries.append(OrderSummaryResponse(
            id=order.id,  # type: ignore
            customer_name=order.customer.name,
            order_total=float(order.order_total),
            status=order.status,
            created_at=order.created_at,  # type: ignore
            item_count=len(order.items)
        ))
    
    return summaries

@app.get("/orders/{order_id}", response_model=OrderResponse)
def get_order(order_id: int):
    """Get specific order details by ID"""
    if order_id not in orders_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with ID {order_id} not found"
        )
    
    order = orders_db[order_id]
    return OrderResponse(
        id=order.id,  # type: ignore
        customer=order.customer,
        items=[item.dict() for item in order.items],
        status=order.status,
        created_at=order.created_at,  # type: ignore
        order_total=float(order.order_total)
    )

@app.put("/orders/{order_id}/status", response_model=OrderResponse)
def update_order_status(order_id: int, status_update: OrderStatusUpdate):
    """Update order status with validation for valid transitions"""
    if order_id not in orders_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with ID {order_id} not found"
        )
    
    order = orders_db[order_id]
    current_status = order.status
    new_status = status_update.status
    
    # Validate status transitions
    valid_transitions = {
        OrderStatus.PENDING: [OrderStatus.CONFIRMED],
        OrderStatus.CONFIRMED: [OrderStatus.READY],
        OrderStatus.READY: [OrderStatus.DELIVERED],
        OrderStatus.DELIVERED: []  # Final state
    }
    
    if new_status not in valid_transitions.get(current_status, []):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status transition from {current_status} to {new_status}"
        )
    
    # Update the status
    order.status = new_status
    orders_db[order_id] = order
    
    return OrderResponse(
        id=order.id,  # type: ignore
        customer=order.customer,
        items=[item.dict() for item in order.items],
        status=order.status,
        created_at=order.created_at,  # type: ignore
        order_total=float(order.order_total)
    )

# Additional order utility endpoints

@app.get("/orders/stats/summary")
def get_orders_summary():
    """Get order statistics and summary"""
    if not orders_db:
        return {"message": "No orders available"}
    
    orders = list(orders_db.values())
    
    # Calculate statistics
    total_orders = len(orders)
    status_counts = {}
    total_revenue = Decimal('0')
    
    for order in orders:
        # Count by status
        status_counts[order.status.value] = status_counts.get(order.status.value, 0) + 1
        # Sum revenue
        total_revenue += order.order_total
    
    # Average order value
    avg_order_value = float(total_revenue / total_orders) if total_orders > 0 else 0
    
    return {
        "total_orders": total_orders,
        "total_revenue": float(total_revenue),
        "average_order_value": round(avg_order_value, 2),
        "status_breakdown": status_counts
    }

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
