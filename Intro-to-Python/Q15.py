# Global list to store books
inventory = []

# Function to add a book
def add_book():
    title = input("Enter book title: ")
    author = input("Enter author name: ")
    inventory.append({'title': title, 'author': author})
    print("Book added successfully!\n")

# Function to search for a book by title
def search_book():
    query = input("Enter book title to search: ")
    found = False
    for book in inventory:
        if book['title'].lower() == query.lower():
            print(f"Found → Book: {book['title']} | Author: {book['author']}\n")
            found = True
            break
    if not found:
        print("Book not found.\n")

# Function to display the inventory
def display_inventory():
    if not inventory:
        print("Inventory is empty.\n")
        return
    print("\nInventory:")
    for book in inventory:
        print(f"- Book: {book['title']} | Author: {book['author']}")
    print()

# Main program loop
def main():
    while True:
        print("1. Add Book")
        print("2. Search Book")
        print("3. Display Inventory")
        print("4. Exit")

        choice = input("Enter your choice (1-4): ")
        print()

        if choice == '1':
            add_book()
        elif choice == '2':
            search_book()
        elif choice == '3':
            display_inventory()
        elif choice == '4':
            print("Exiting Library System. Goodbye!")
            break
        else:
            print("Invalid choice. Please select from 1 to 4.\n")

# Run the program
main()