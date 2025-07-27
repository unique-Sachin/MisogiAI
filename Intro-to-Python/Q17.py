# 1. Simple list creation: squares of numbers 0-9
squares = [x**2 for x in range(10)]
print('Squares:', squares)

# 2. Filtering: only even numbers from 0-19
# Traditional: evens = []
# for x in range(20):
#     if x % 2 == 0:
#         evens.append(x)
evans = [x for x in range(20) if x % 2 == 0]
print('Evens:', evans)

# 3. Nested loops: all (i, j) pairs for i in 0-2, j in 0-2
pairs = [(i, j) for i in range(3) for j in range(3)]
print('Pairs:', pairs)

# 4. Matrix flattening: flatten a 2D list
matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
flattened = [num for row in matrix for num in row]
print('Flattened:', flattened)
