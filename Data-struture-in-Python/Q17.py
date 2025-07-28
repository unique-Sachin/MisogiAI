employees = [
    ("Alice", 50000, "Engineering"),
    ("Bob", 60000, "Marketing"),
    ("Carol", 55000, "Engineering"),
    ("David", 45000, "Sales")
]

from pprint import pprint  # For cleaner printing

# Make a copy to preserve original
original_employees = employees.copy()

# 1. Sort by Salary - Ascending and Descending (using sorted)
by_salary_asc = sorted(employees, key=lambda emp: emp[1])
by_salary_desc = sorted(employees, key=lambda emp: emp[1], reverse=True)

print("Sorted by Salary (Ascending):")
pprint(by_salary_asc)
print("\nSorted by Salary (Descending):")
pprint(by_salary_desc)
print()

# 2. Sort by Department, Then by Salary (using sorted)
by_dept_then_salary = sorted(employees, key=lambda emp: (emp[2], emp[1]))
print("Sorted by Department, then by Salary:")
pprint(by_dept_then_salary)
print()

# 3. Create a Reversed List (without modifying original)
reversed_list = list(reversed(employees))
print("Reversed Employee List (original unchanged):")
pprint(reversed_list)
print()

# 4. Sort by Name Length (using .sort to modify in-place)
employees.sort(key=lambda emp: len(emp[0]))
print("Employees Sorted by Name Length (Modified Original):")
pprint(employees)
print()

# 5. Demonstrate .sort() vs sorted()
# - .sort() modifies list in-place (done above for name length)
# - sorted() creates a new list (used above for salary, dept)
print("Original List After .sort() by Name Length:")
pprint(employees)
print("\nUnmodified Copy of Original List (Before Any .sort()):")
pprint(original_employees)