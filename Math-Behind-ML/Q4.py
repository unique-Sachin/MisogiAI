"""
mlmath: A simple math library for machine learning operations.

Functions:
- dot_product(a, b): Compute the dot product of two vectors.
- matrix_multiply(A, B): Multiply two matrices.
- conditional_probability(events): Compute conditional probability from a dictionary of event counts.
"""

def dot_product(a, b):
    """
    Compute the dot product of two vectors.
    
    Args:
        a (list of numbers): First vector.
        b (list of numbers): Second vector.
    Returns:
        number: The dot product of a and b.
    Example:
        >>> dot_product([1, 2, 3], [4, 5, 6])
        32
    """
    return sum(x * y for x, y in zip(a, b))

def matrix_multiply(A, B):
    """
    Multiply two matrices A and B.
    
    Args:
        A (list of list of numbers): First matrix.
        B (list of list of numbers): Second matrix.
    Returns:
        list of list of numbers: The matrix product.
    Example:
        >>> matrix_multiply([[1, 2], [3, 4]], [[5, 6], [7, 8]])
        [[19, 22], [43, 50]]
    """
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

def conditional_probability(events):
    """
    Compute conditional probability P(A|B) = P(A and B) / P(B) from event counts.
    
    Args:
        events (dict): Dictionary with keys 'A_and_B' and 'B', or 'A_and_B', 'B', and 'total'.
            - 'A_and_B': Count of both A and B occurring.
            - 'B': Count of B occurring.
            - 'total' (optional): Total number of trials (for probability calculation).
    Returns:
        float: The conditional probability P(A|B).
    Example:
        >>> conditional_probability({'A_and_B': 120, 'B': 400})
        0.3
    """
    A_and_B = events.get('A_and_B')
    B = events.get('B')
    if B == 0:
        raise ValueError("Count for event B must be greater than zero.")
    return A_and_B / B

# Example usage
if __name__ == "__main__":
    print("dot_product([1, 2, 3], [4, 5, 6]) =", dot_product([1, 2, 3], [4, 5, 6]))
    print("matrix_multiply([[1, 2], [3, 4]], [[5, 6], [7, 8]]) =", matrix_multiply([[1, 2], [3, 4]], [[5, 6], [7, 8]]))
    print("conditional_probability({'A_and_B': 120, 'B': 400}) =", conditional_probability({'A_and_B': 120, 'B': 400}))
