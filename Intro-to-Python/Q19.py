name = "Alice"
age = 28
city = "Delhi"

# 1. % formatting
print("My name is %s, I am %d years old, and I live in %s." % (name, age, city))

# 2. .format() method
print("My name is {}, I am {} years old, and I live in {}.".format(name, age, city))

# 3. f-string
print(f"My name is {name}, I am {age} years old, and I live in {city}.")
