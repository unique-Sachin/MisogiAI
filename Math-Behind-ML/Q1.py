# Vector Operations

def add_vectors(a, b):
    """Add two vectors element-wise."""
    return [x + y for x, y in zip(a, b)]

def dot_product(a, b):
    """Compute the dot product of two vectors."""
    return sum(x * y for x, y in zip(a, b))

def are_orthogonal(a, b):
    """Check if two vectors are orthogonal (dot product is zero)."""
    return dot_product(a, b) == 0

# Matrix Multiplication

def multiply_matrices(A, B):
    """Multiply two matrices A and B using nested loops."""
    result = []
    num_rows_A = len(A)
    num_cols_A = len(A[0])
    num_cols_B = len(B[0])
    for i in range(num_rows_A):
        row = []
        for j in range(num_cols_B):
            s = 0
            for k in range(num_cols_A):
                s += A[i][k] * B[k][j]
            row.append(s)
        result.append(row)
    return result

# Sample Input for Vector Operations
a = [1, 2, 3]
b = [4, 5, 6]

print("Sum:", add_vectors(a, b))
print("Dot Product:", dot_product(a, b))
print("Orthogonal:", are_orthogonal(a, b))

# Sample Input for Matrix Multiplication
A = [[1, 2], [3, 4]]
B = [[5, 6], [7, 8]]

print("Matrix Product:")
product = multiply_matrices(A, B)
for row in product:
    print(row)
