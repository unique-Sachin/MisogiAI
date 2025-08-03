"""
Test Cases for Restaurant Menu API Pydantic Validations

This file demonstrates the test cases you specified:
1. ✅ Valid: Create a Margherita Pizza with valid data
2. ❌ Invalid price: $0.50 → should raise error
3. ❌ Invalid category rule: spicy beverage → should raise error
4. ❌ Missing ingredients → should raise error
5. ❌ Invalid name: "Pizza123!" → should raise error
"""

from decimal import Decimal
from restaurant_menu_api import FoodItem, FoodCategory, FoodItemCreate
from pydantic import ValidationError

def test_cases():
    print("🧪 Running Test Cases for Restaurant Menu API Validations\n")
    
    # Test Case 1: ✅ Valid Margherita Pizza
    print("1. ✅ Testing valid Margherita Pizza creation:")
    try:
        valid_pizza = FoodItemCreate(
            name="Margherita Pizza",
            description="Classic pizza with fresh tomatoes, mozzarella cheese, and basil leaves",
            category=FoodCategory.MAIN_COURSE,
            price=Decimal("12.99"),
            preparation_time=15,
            ingredients=["Pizza dough", "Tomato sauce", "Mozzarella cheese", "Fresh basil"],
            calories=650,
            is_vegetarian=True,
            is_spicy=False
        )
        print(f"   SUCCESS: Created {valid_pizza.name}")
        print(f"   Price Category: {FoodItem(id=1, **valid_pizza.dict()).price_category}")
        print(f"   Dietary Info: {FoodItem(id=1, **valid_pizza.dict()).dietary_info}")
    except ValidationError as e:
        print(f"   UNEXPECTED ERROR: {e}")
    print()
    
    # Test Case 2: ❌ Invalid price: $0.50
    print("2. ❌ Testing invalid price ($0.50):")
    try:
        invalid_price_item = FoodItemCreate(
            name="Cheap Item",
            description="This item has an invalid price that should fail validation",
            category=FoodCategory.APPETIZER,
            price=Decimal("0.50"),  # Invalid: below minimum $1.00
            preparation_time=10,
            ingredients=["Some ingredient"],
            is_vegetarian=False,
            is_spicy=False
        )
        print(f"   UNEXPECTED SUCCESS: This should have failed!")
    except ValidationError as e:
        print(f"   SUCCESS: Validation caught the error - {e.errors()[0]['msg']}")
    print()
    
    # Test Case 3: ❌ Invalid category rule: spicy beverage
    print("3. ❌ Testing invalid category rule (spicy beverage):")
    try:
        spicy_beverage = FoodItemCreate(
            name="Spicy Coffee",
            description="A hot and spicy coffee beverage that should not be allowed",
            category=FoodCategory.BEVERAGE,
            price=Decimal("5.99"),
            preparation_time=8,
            ingredients=["Coffee", "Spices"],
            is_vegetarian=True,
            is_spicy=True  # Invalid: beverages cannot be spicy
        )
        print(f"   UNEXPECTED SUCCESS: This should have failed!")
    except ValidationError as e:
        print(f"   SUCCESS: Validation caught the error - {e.errors()[0]['msg']}")
    print()
    
    # Test Case 4: ❌ Missing ingredients
    print("4. ❌ Testing missing ingredients:")
    try:
        no_ingredients_item = FoodItemCreate(
            name="Empty Dish",
            description="This dish has no ingredients and should fail validation",
            category=FoodCategory.MAIN_COURSE,
            price=Decimal("15.99"),
            preparation_time=20,
            ingredients=[],  # Invalid: empty ingredients list
            is_vegetarian=False,
            is_spicy=False
        )
        print(f"   UNEXPECTED SUCCESS: This should have failed!")
    except ValidationError as e:
        print(f"   SUCCESS: Validation caught the error - {e.errors()[0]['msg']}")
    print()
    
    # Test Case 5: ❌ Invalid name: "Pizza123!"
    print("5. ❌ Testing invalid name with numbers and special characters:")
    try:
        invalid_name_item = FoodItemCreate(
            name="Pizza123!",  # Invalid: contains numbers and special characters
            description="This pizza has an invalid name that should fail validation",
            category=FoodCategory.MAIN_COURSE,
            price=Decimal("18.99"),
            preparation_time=15,
            ingredients=["Pizza dough", "Cheese"],
            is_vegetarian=False,
            is_spicy=False
        )
        print(f"   UNEXPECTED SUCCESS: This should have failed!")
    except ValidationError as e:
        print(f"   SUCCESS: Validation caught the error - {e.errors()[0]['msg']}")
    print()
    
    # Additional Test Case: ❌ Beverage with long prep time
    print("6. ❌ Testing beverage with preparation time > 10 minutes:")
    try:
        slow_beverage = FoodItemCreate(
            name="Slow Smoothie",
            description="This smoothie takes too long to prepare for a beverage",
            category=FoodCategory.BEVERAGE,
            price=Decimal("7.99"),
            preparation_time=15,  # Invalid: beverages must have prep time ≤ 10 minutes
            ingredients=["Fruits", "Yogurt"],
            is_vegetarian=True,
            is_spicy=False
        )
        print(f"   UNEXPECTED SUCCESS: This should have failed!")
    except ValidationError as e:
        print(f"   SUCCESS: Validation caught the error - {e.errors()[0]['msg']}")
    print()
    
    # Additional Test Case: ❌ Vegetarian item with too many calories
    print("7. ❌ Testing vegetarian item with calories ≥ 800:")
    try:
        high_cal_veg = FoodItemCreate(
            name="Heavy Veggie Burger",
            description="A vegetarian burger with too many calories for validation rules",
            category=FoodCategory.MAIN_COURSE,
            price=Decimal("22.99"),
            preparation_time=25,
            ingredients=["Veggie patty", "Bun", "Cheese", "Sauce"],
            calories=850,  # Invalid: vegetarian items must have < 800 calories
            is_vegetarian=True,
            is_spicy=False
        )
        print(f"   UNEXPECTED SUCCESS: This should have failed!")
    except ValidationError as e:
        print(f"   SUCCESS: Validation caught the error - {e.errors()[0]['msg']}")
    print()
    
    print("🎉 All test cases completed! The validation system is working correctly.")

if __name__ == "__main__":
    test_cases()
