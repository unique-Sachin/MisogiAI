# Data structures
fruits_list = ["apple", "banana", "orange", "apple", "grape"]
fruits_tuple = ("apple", "banana", "orange")
fruits_set = {"apple", "banana", "orange", "grape"}
fruits_dict = {"apple": 5, "banana": 3, "orange": 8, "grape": 2}

# 1. Check for Membership
print("Membership check for 'apple':")
print("In list:", "apple" in fruits_list)
print("In tuple:", "apple" in fruits_tuple)
print("In set:", "apple" in fruits_set)
print("In dict (as key):", "apple" in fruits_dict)
print()

# 2. Find Length
print("Length of each structure:")
print("List:", len(fruits_list))
print("Tuple:", len(fruits_tuple))
print("Set:", len(fruits_set))
print("Dict:", len(fruits_dict))
print()

# 3. Iterate and Print Elements
print("Iterating through list:")
for fruit in fruits_list:
    print(fruit)
print()

print("Iterating through tuple:")
for fruit in fruits_tuple:
    print(fruit)
print()

print("Iterating through set:")
for fruit in fruits_set:
    print(fruit)
print()

print("Iterating through dict (keys and values):")
for fruit, count in fruits_dict.items():
    print(f"{fruit}: {count}")
print()

# 4. Compare Membership Testing Performance
print("""
Performance Explanation:
- Sets and dictionaries use hash tables, so membership checks (e.g., 'apple' in fruits_set) are on average O(1) time complexity.
- Lists and tuples require scanning each element, so membership checks are O(n) time complexity.
- Therefore, sets and dicts are more efficient for membership testing, especially with large data.
""")

# 5. Demonstrate Different Iteration Patterns
print("Different iteration patterns:")
print("For item in set:")
for fruit in fruits_set:
    print(fruit)
print("For key in dict:")
for fruit in fruits_dict:
    print(fruit)
print("For key, value in dict.items():")
for fruit, count in fruits_dict.items():
    print(f"{fruit}: {count}")
