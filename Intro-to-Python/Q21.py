# Custom map function
def custom_map(func, iterable):
    return [func(x) for x in iterable]

# Custom filter function
def custom_filter(func, iterable):
    return [x for x in iterable if func(x)]

# Custom reduce function
def custom_reduce(func, iterable):
    result = iterable[0]
    for x in iterable[1:]:
        result = func(result, x)
    return result

# Demonstrations
lst = [1, 2, 3, 4]

# 1. custom_map: double each element
print('custom_map:', custom_map(lambda x: x * 2, lst))  # [2, 4, 6, 8]

# 2. custom_filter: keep even numbers
print('custom_filter:', custom_filter(lambda x: x % 2 == 0, lst))  # [2, 4]

# 3. custom_reduce: sum all elements
print('custom_reduce:', custom_reduce(lambda x, y: x + y, lst))  # 10
