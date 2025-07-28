# Simple Shopping Cart Simulation

def add_item(cart, item):
    cart.append(item)
    print(f'Added: {item}')

def remove_item(cart, item):
    if item in cart:
        cart.remove(item)
        print(f'Removed: {item}')
    else:
        print(f'Item not found: {item}')

def remove_last_item(cart):
    if cart:
        removed = cart.pop()
        print(f'Removed last item: {removed}')
    else:
        print('Cart is empty. Nothing to remove.')

def display_sorted(cart):
    print('Cart items (sorted):', sorted(cart))

def display_with_indices(cart):
    print('Cart contents:')
    for idx, item in enumerate(cart):
        print(f'{idx}: {item}')

# --- Sample Operations ---
cart = []

# Add items: "apples", "bread", "milk", "eggs"
add_item(cart, "apples")
add_item(cart, "bread")
add_item(cart, "milk")
add_item(cart, "eggs")

# Remove "bread"
remove_item(cart, "bread")

# Remove the last added item
remove_last_item(cart)

# Sort and display items alphabetically
display_sorted(cart)

# Display final cart with index numbers
display_with_indices(cart)
