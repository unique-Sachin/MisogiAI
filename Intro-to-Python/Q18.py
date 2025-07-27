# 1. Square of even numbers from 1 to 10
print([i*i for i in range(1, 11) if i % 2 == 0])

# 2. Capitalize all words in a list
print(list(map(str.capitalize, ['hello', 'world'])))

# 3. Sum of all numbers in a list using reduce
from functools import reduce
print(reduce(lambda x, y: x + y, [1, 2, 3, 4]))

# 4. Filter out vowels from a string
print(list(filter(lambda c: c.lower() not in 'aeiou', 'Hello World')))

# 5. Flatten a 2D list
matrix = [[1, 2], [3, 4], [5, 6]]
print([item for sublist in matrix for item in sublist])

# 6. Get lengths of words longer than 3 letters
words = ['hi', 'hello', 'world', 'a', 'python']
print(list(map(len, filter(lambda w: len(w) > 3, words))))
