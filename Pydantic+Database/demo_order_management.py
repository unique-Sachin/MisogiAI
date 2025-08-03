#!/usr/bin/env python3
"""
Order Management System Demo Script

This script demonstrates all the features of the order management system
including creating orders, updating status, and handling validation errors.
Make sure the server is running (python restaurant_menu_api.py) before executing this script.
"""

import requests
import json
from decimal import Decimal

BASE_URL = "http://localhost:8000"

def print_section(title):
    print(f"\n{'='*60}")
    print(f"📦 {title}")
    print('='*60)

def print_response(response, title=""):
    if title:
        print(f"\n📋 {title}")
    print("-" * 40)
    if response.status_code in [200, 201]:
        print(f"✅ Status: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"❌ Status: {response.status_code}")
        print(json.dumps(response.json(), indent=2))

def demo_order_management():
    print("🚀 Order Management System Demo")
    print("="*60)
    
    # 1. Create valid order
    print_section("1. CREATE VALID ORDER")
    valid_order = {
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
    }
    response = requests.post(f"{BASE_URL}/orders", json=valid_order)
    print_response(response, "Created Order with 2 Items")
    
    if response.status_code == 201:
        order_id = response.json()["id"]
        print(f"\n🔖 Order ID: {order_id} (will be used in subsequent tests)")
    
    # 2. Create another order for testing
    print_section("2. CREATE SECOND ORDER")
    second_order = {
        "customer": {
            "name": "Bob Wilson",
            "phone": "5559876543",
            "address": "456 Elm Street, Springfield"
        },
        "items": [
            {
                "menu_item_id": 3,
                "menu_item_name": "Caesar Salad",
                "quantity": 1,
                "unit_price": "7.50"
            },
            {
                "menu_item_id": 4,
                "menu_item_name": "Chocolate Lava Cake",
                "quantity": 2,
                "unit_price": "6.99"
            }
        ]
    }
    response = requests.post(f"{BASE_URL}/orders", json=second_order)
    print_response(response, "Created Second Order")
    
    # 3. Get all orders
    print_section("3. GET ALL ORDERS")
    response = requests.get(f"{BASE_URL}/orders")
    print_response(response, "All Orders Summary")
    
    # 4. Get specific order
    print_section("4. GET SPECIFIC ORDER")
    response = requests.get(f"{BASE_URL}/orders/1")
    print_response(response, "Order #1 Details")
    
    # 5. Update order status (valid transition)
    print_section("5. UPDATE ORDER STATUS (Valid)")
    status_update = {"status": "confirmed"}
    response = requests.put(f"{BASE_URL}/orders/1/status", json=status_update)
    print_response(response, "Updated Status to CONFIRMED")
    
    # 6. Update order status (another valid transition)
    print_section("6. CONTINUE STATUS PROGRESSION")
    status_update = {"status": "ready"}
    response = requests.put(f"{BASE_URL}/orders/1/status", json=status_update)
    print_response(response, "Updated Status to READY")
    
    # 7. Complete the order
    print_section("7. COMPLETE ORDER")
    status_update = {"status": "delivered"}
    response = requests.put(f"{BASE_URL}/orders/1/status", json=status_update)
    print_response(response, "Updated Status to DELIVERED")
    
    # 8. Try invalid status transition
    print_section("8. INVALID STATUS TRANSITION")
    status_update = {"status": "pending"}  # Can't go back from delivered
    response = requests.put(f"{BASE_URL}/orders/1/status", json=status_update)
    print_response(response, "Attempted Invalid Status Transition")
    
    # 9. Validation Error: Empty items
    print_section("9. VALIDATION ERROR - Empty Items")
    empty_order = {
        "customer": {
            "name": "Charlie Brown",
            "phone": "5551234567",
            "address": "789 Peanuts Lane"
        },
        "items": []  # Invalid: empty items
    }
    response = requests.post(f"{BASE_URL}/orders", json=empty_order)
    print_response(response, "Order with Empty Items")
    
    # 10. Validation Error: Invalid phone
    print_section("10. VALIDATION ERROR - Invalid Phone")
    invalid_phone_order = {
        "customer": {
            "name": "Diana Prince",
            "phone": "123456789",  # Invalid: only 9 digits
            "address": "123 Hero Lane"
        },
        "items": [
            {
                "menu_item_id": 1,
                "menu_item_name": "Hero Sandwich",
                "quantity": 1,
                "unit_price": "12.99"
            }
        ]
    }
    response = requests.post(f"{BASE_URL}/orders", json=invalid_phone_order)
    print_response(response, "Order with Invalid Phone")
    
    # 11. Validation Error: Quantity too large
    print_section("11. VALIDATION ERROR - Large Quantity")
    large_quantity_order = {
        "customer": {
            "name": "Eve Adams",
            "phone": "5551234567",
            "address": "321 Apple Street"
        },
        "items": [
            {
                "menu_item_id": 1,
                "menu_item_name": "Pizza Party",
                "quantity": 15,  # Invalid: exceeds maximum of 10
                "unit_price": "15.99"
            }
        ]
    }
    response = requests.post(f"{BASE_URL}/orders", json=large_quantity_order)
    print_response(response, "Order with Large Quantity")
    
    # 12. Validation Error: Invalid menu item ID
    print_section("12. VALIDATION ERROR - Invalid Menu Item ID")
    invalid_id_order = {
        "customer": {
            "name": "Frank Miller",
            "phone": "5551234567",
            "address": "987 Comic Street"
        },
        "items": [
            {
                "menu_item_id": -1,  # Invalid: negative ID
                "menu_item_name": "Invalid Item",
                "quantity": 1,
                "unit_price": "10.00"
            }
        ]
    }
    response = requests.post(f"{BASE_URL}/orders", json=invalid_id_order)
    print_response(response, "Order with Invalid Menu Item ID")
    
    # 13. Test non-existent order
    print_section("13. ERROR HANDLING - Non-existent Order")
    response = requests.get(f"{BASE_URL}/orders/999")
    print_response(response, "Attempted to Get Non-existent Order")
    
    # 14. Orders statistics
    print_section("14. ORDER STATISTICS")
    response = requests.get(f"{BASE_URL}/orders/stats/summary")
    print_response(response, "Order Statistics Summary")
    
    # 15. Demonstrate computed properties
    print_section("15. COMPUTED PROPERTIES DEMO")
    print("📊 Notice how each order automatically includes:")
    print("   • item_total: quantity × unit_price for each item")
    print("   • order_total: sum of all item totals")
    print("   • Automatic timestamp generation")
    print("   • Status progression validation")
    
    # Get current orders to show computed properties
    response = requests.get(f"{BASE_URL}/orders")
    if response.status_code == 200:
        orders = response.json()
        print("\n🧮 Current Orders with Computed Properties:")
        for order in orders:
            print(f"   • Order #{order['id']}: {order['customer_name']} - ${order['order_total']} ({order['status']})")
    
    print_section("DEMO COMPLETE")
    print("✨ All order management features demonstrated successfully!")
    print("🔗 Integration with menu system complete")
    print("🌐 Visit http://localhost:8000/docs for interactive API documentation")
    print("📊 Order and menu systems working together seamlessly")

if __name__ == "__main__":
    try:
        demo_order_management()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the API server.")
        print("🚀 Please start the server first by running:")
        print("   python restaurant_menu_api.py")
    except Exception as e:
        print(f"❌ Error: {e}")
