# Mathematical calculations
square = lambda x: x * x
print('square(5):', square(5))  # 25

# Factorial approximation (using reduce)
from functools import reduce
factorial = lambda n: reduce(lambda x, y: x * y, range(1, n+1), 1)
print('factorial(5):', factorial(5))  # 120

# String manipulations
reverse = lambda s: s[::-1]
print("reverse('hello'):", reverse('hello'))  # 'olleh'

uppercase = lambda s: s.upper()
print("uppercase('hello'):", uppercase('hello'))  # 'HELLO'

# List operations
filter_evens = lambda lst: list(filter(lambda x: x % 2 == 0, lst))
print('filter_evens([1,2,3,4,5,6]):', filter_evens([1,2,3,4,5,6]))  # [2, 4, 6]

sum_list = lambda lst: sum(lst)
print('sum_list([1,2,3,4]):', sum_list([1,2,3,4]))  # 10
