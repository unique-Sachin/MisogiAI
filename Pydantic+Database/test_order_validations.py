"""
Test Cases for Order Management System

This file demonstrates the test cases for the order management functionality:
1. ✅ Valid Order: Create order with 2 items
2. ❌ Empty Items: Order with empty items → should fail
3. ❌ Invalid Phone: Customer phone not 10 digits → should fail
4. ❌ Large Quantity: quantity = 15 → should fail
5. ✅ Status Update: Change from PENDING to CONFIRMED
"""

from decimal import Decimal
from restaurant_menu_api import (
    OrderCreate, OrderItemCreate, CustomerCreate, OrderStatusUpdate,
    OrderStatus, Order, OrderItem, Customer
)
from pydantic import ValidationError

def test_order_cases():
    print("🧪 Running Test Cases for Order Management System\n")
    
    # Test Case 1: ✅ Valid Order with 2 items
    print("1. ✅ Testing valid order creation with 2 items:")
    try:
        valid_order = OrderCreate(
            customer=CustomerCreate(
                name="Alice Smith",
                phone="5551234567",
                address="123 Oak Street, Springfield"
            ),
            items=[
                OrderItemCreate(
                    menu_item_id=1,
                    menu_item_name="Margherita Pizza",
                    quantity=1,
                    unit_price=Decimal("15.99")
                ),
                OrderItemCreate(
                    menu_item_id=2,
                    menu_item_name="Spicy Chicken Wings",
                    quantity=2,
                    unit_price=Decimal("12.50")
                )
            ]
        )
        
        # Create the actual order to test computed properties
        order_items = [OrderItem(**item.model_dump()) for item in valid_order.items]
        customer = Customer(**valid_order.customer.model_dump())
        test_order = Order(id=1, customer=customer, items=order_items)
        
        print(f"   SUCCESS: Created order for {valid_order.customer.name}")
        print(f"   Items: {len(valid_order.items)} items")
        print(f"   Order Total: ${test_order.order_total}")
        print(f"   Customer Phone: {valid_order.customer.phone}")
    except ValidationError as e:
        print(f"   UNEXPECTED ERROR: {e}")
    print()
    
    # Test Case 2: ❌ Empty Items
    print("2. ❌ Testing order with empty items:")
    try:
        empty_items_order = OrderCreate(
            customer=CustomerCreate(
                name="Bob Johnson",
                phone="5551234567",
                address="456 Pine Street"
            ),
            items=[]  # Invalid: empty items list
        )
        print(f"   UNEXPECTED SUCCESS: This should have failed!")
    except ValidationError as e:
        print(f"   SUCCESS: Validation caught the error - {e.errors()[0]['msg']}")
    print()
    
    # Test Case 3: ❌ Invalid Phone (not 10 digits)
    print("3. ❌ Testing invalid customer phone number:")
    try:
        invalid_phone_order = OrderCreate(
            customer=CustomerCreate(
                name="Charlie Brown",
                phone="123456789",  # Invalid: only 9 digits
                address="789 Elm Street"
            ),
            items=[
                OrderItemCreate(
                    menu_item_id=1,
                    menu_item_name="Caesar Salad",
                    quantity=1,
                    unit_price=Decimal("9.99")
                )
            ]
        )
        print(f"   UNEXPECTED SUCCESS: This should have failed!")
    except ValidationError as e:
        print(f"   SUCCESS: Validation caught the error - {e.errors()[0]['msg']}")
    print()
    
    # Test Case 4: ❌ Large Quantity (> 10)
    print("4. ❌ Testing invalid quantity (> 10):")
    try:
        large_quantity_order = OrderCreate(
            customer=CustomerCreate(
                name="Diana Prince",
                phone="5551234567",
                address="321 Hero Lane"
            ),
            items=[
                OrderItemCreate(
                    menu_item_id=1,
                    menu_item_name="Chocolate Cake",
                    quantity=15,  # Invalid: exceeds maximum of 10
                    unit_price=Decimal("6.99")
                )
            ]
        )
        print(f"   UNEXPECTED SUCCESS: This should have failed!")
    except ValidationError as e:
        print(f"   SUCCESS: Validation caught the error - {e.errors()[0]['msg']}")
    print()
    
    # Test Case 5: ✅ Valid Status Update
    print("5. ✅ Testing valid status update:")
    try:
        status_update = OrderStatusUpdate(status=OrderStatus.CONFIRMED)
        print(f"   SUCCESS: Created status update to {status_update.status}")
        
        # Test invalid status update as well
        print("   Testing invalid status update (PENDING to DELIVERED):")
        try:
            invalid_status = OrderStatusUpdate(status=OrderStatus.DELIVERED)
            # This should be caught at the business logic level, not Pydantic
            print(f"   Note: Pydantic allows this, but business logic should prevent PENDING→DELIVERED")
        except ValidationError as e:
            print(f"   Validation error: {e.errors()[0]['msg']}")
    except ValidationError as e:
        print(f"   UNEXPECTED ERROR: {e}")
    print()
    
    # Additional Test Case: ❌ Invalid menu item ID (negative)
    print("6. ❌ Testing invalid menu item ID (negative):")
    try:
        invalid_id_order = OrderCreate(
            customer=CustomerCreate(
                name="Eve Adams",
                phone="5551234567",
                address="654 Oak Avenue"
            ),
            items=[
                OrderItemCreate(
                    menu_item_id=-1,  # Invalid: negative ID
                    menu_item_name="Invalid Item",
                    quantity=1,
                    unit_price=Decimal("10.00")
                )
            ]
        )
        print(f"   UNEXPECTED SUCCESS: This should have failed!")
    except ValidationError as e:
        print(f"   SUCCESS: Validation caught the error - {e.errors()[0]['msg']}")
    print()
    
    # Additional Test Case: ❌ Invalid unit price (negative)
    print("7. ❌ Testing invalid unit price (negative):")
    try:
        invalid_price_order = OrderCreate(
            customer=CustomerCreate(
                name="Frank Miller",
                phone="5551234567",
                address="987 Maple Street"
            ),
            items=[
                OrderItemCreate(
                    menu_item_id=1,
                    menu_item_name="Free Item",
                    quantity=1,
                    unit_price=Decimal("-5.00")  # Invalid: negative price
                )
            ]
        )
        print(f"   UNEXPECTED SUCCESS: This should have failed!")
    except ValidationError as e:
        print(f"   SUCCESS: Validation caught the error - {e.errors()[0]['msg']}")
    print()
    
    # Test Case: ✅ Computed Properties Demo
    print("8. ✅ Testing computed properties:")
    try:
        # Create order items
        item1 = OrderItem(
            menu_item_id=1,
            menu_item_name="Pizza",
            quantity=2,
            unit_price=Decimal("15.99")
        )
        item2 = OrderItem(
            menu_item_id=2,
            menu_item_name="Wings",
            quantity=1,
            unit_price=Decimal("8.99")
        )
        
        customer = Customer(
            name="Grace Hopper",
            phone="5551234567",
            address="123 Computer Lane"
        )
        
        order = Order(
            id=999,
            customer=customer,
            items=[item1, item2]
        )
        
        print(f"   Item 1 Total: ${item1.item_total} (${item1.unit_price} × {item1.quantity})")
        print(f"   Item 2 Total: ${item2.item_total} (${item2.unit_price} × {item2.quantity})")
        print(f"   Order Total: ${order.order_total}")
        print(f"   Order Status: {order.status}")
        
    except Exception as e:
        print(f"   ERROR: {e}")
    print()
    
    print("🎉 All order management test cases completed!")

if __name__ == "__main__":
    test_order_cases()
