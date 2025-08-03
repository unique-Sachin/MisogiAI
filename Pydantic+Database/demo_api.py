#!/usr/bin/env python3
"""
Restaurant Menu API Demo Script

This script demonstrates all the key features and endpoints of the restaurant menu API.
Make sure the server is running (python restaurant_menu_api.py) before executing this script.
"""

import requests
import json
from decimal import Decimal

BASE_URL = "http://localhost:8000"

def print_section(title):
    print(f"\n{'='*60}")
    print(f"🍽️  {title}")
    print('='*60)

def print_response(response, title=""):
    if title:
        print(f"\n📋 {title}")
    print("-" * 40)
    if response.status_code == 200 or response.status_code == 201:
        print(f"✅ Status: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"❌ Status: {response.status_code}")
        print(json.dumps(response.json(), indent=2))

def demo_api():
    print("🚀 Restaurant Menu API Demo")
    print("="*60)
    
    # 1. Get all menu items
    print_section("1. GET ALL MENU ITEMS")
    response = requests.get(f"{BASE_URL}/menu")
    print_response(response, "All Menu Items")
    
    # 2. Get specific item
    print_section("2. GET SPECIFIC ITEM")
    response = requests.get(f"{BASE_URL}/menu/1")
    print_response(response, "Margherita Pizza Details")
    
    # 3. Get items by category
    print_section("3. FILTER BY CATEGORY")
    response = requests.get(f"{BASE_URL}/menu/category/appetizer")
    print_response(response, "Appetizer Items")
    
    # 4. Create valid new item
    print_section("4. CREATE NEW ITEM (Valid)")
    new_item = {
        "name": "Thai Green Curry",
        "description": "Authentic Thai green curry with coconut milk, vegetables, and aromatic herbs",
        "category": "main_course",
        "price": 16.99,
        "preparation_time": 22,
        "ingredients": ["Green curry paste", "Coconut milk", "Vegetables", "Thai basil", "Rice"],
        "calories": 520,
        "is_vegetarian": True,
        "is_spicy": True
    }
    response = requests.post(f"{BASE_URL}/menu", json=new_item)
    print_response(response, "Created Thai Green Curry")
    
    # 5. Try to create invalid item (spicy dessert)
    print_section("5. VALIDATION ERROR - Spicy Dessert")
    invalid_item = {
        "name": "Spicy Ice Cream",
        "description": "Ice cream with hot sauce that should fail validation",
        "category": "dessert",
        "price": 8.99,
        "preparation_time": 5,
        "ingredients": ["Ice cream", "Hot sauce"],
        "is_vegetarian": True,
        "is_spicy": True  # This should fail - desserts can't be spicy
    }
    response = requests.post(f"{BASE_URL}/menu", json=invalid_item)
    print_response(response, "Validation Error Example")
    
    # 6. Try invalid price
    print_section("6. VALIDATION ERROR - Invalid Price")
    invalid_price_item = {
        "name": "Cheap Soup",
        "description": "A soup with invalid pricing below minimum",
        "category": "appetizer",
        "price": 0.50,  # Below minimum $1.00
        "preparation_time": 10,
        "ingredients": ["Water", "Salt"],
        "is_vegetarian": True,
        "is_spicy": False
    }
    response = requests.post(f"{BASE_URL}/menu", json=invalid_price_item)
    print_response(response, "Invalid Price Error")
    
    # 7. Try invalid name
    print_section("7. VALIDATION ERROR - Invalid Name")
    invalid_name_item = {
        "name": "Pizza123!",  # Contains numbers and special chars
        "description": "Pizza with invalid name containing numbers and symbols",
        "category": "main_course",
        "price": 15.99,
        "preparation_time": 20,
        "ingredients": ["Dough", "Cheese"],
        "is_vegetarian": True,
        "is_spicy": False
    }
    response = requests.post(f"{BASE_URL}/menu", json=invalid_name_item)
    print_response(response, "Invalid Name Error")
    
    # 8. Update an item
    print_section("8. UPDATE ITEM")
    update_data = {
        "price": 13.99,
        "is_available": True,
        "calories": 680
    }
    response = requests.put(f"{BASE_URL}/menu/1", json=update_data)
    print_response(response, "Updated Margherita Pizza")
    
    # 9. Get menu statistics
    print_section("9. MENU STATISTICS")
    response = requests.get(f"{BASE_URL}/menu/stats/summary")
    print_response(response, "Menu Statistics & Summary")
    
    # 10. Delete an item
    print_section("10. DELETE ITEM")
    response = requests.delete(f"{BASE_URL}/menu/6")  # Delete the salmon we created earlier
    print_response(response, "Deleted Item")
    
    # 11. Demonstrate computed properties
    print_section("11. COMPUTED PROPERTIES DEMO")
    print("📊 Notice how each item automatically includes:")
    print("   • price_category: Budget/Mid-range/Premium based on price")
    print("   • dietary_info: Dynamic tags like ['Vegetarian', 'Spicy', 'Low Calorie']")
    
    # Get an updated menu to show final state
    response = requests.get(f"{BASE_URL}/menu")
    if response.status_code == 200:
        items = response.json()
        print("\n🏷️  Current Menu with Computed Properties:")
        for item in items:
            print(f"   • {item['name']}: {item['price_category']} - {item['dietary_info']}")
    
    print_section("DEMO COMPLETE")
    print("✨ All features demonstrated successfully!")
    print("🌐 Visit http://localhost:8000/docs for interactive API documentation")
    print("📖 Check README.md for detailed information")

if __name__ == "__main__":
    try:
        demo_api()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the API server.")
        print("🚀 Please start the server first by running:")
        print("   python restaurant_menu_api.py")
    except Exception as e:
        print(f"❌ Error: {e}")
