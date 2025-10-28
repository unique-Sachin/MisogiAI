# A user tries to withdraw more money than available.

# It raises a ValueError but wraps it inside a custom exception InsufficientFundsError.

# Demonstrate raise ... from ... exception chaining.


class Bank:
    def __init__(self,total) -> None:
        self.total = total
    
    def add_money(self,amount):
        self.total += amount
    
    def withdraw_money(self,amount):
        if amount>self.total:
            raise ValueError("InsufficientFunds")
        else:
            self.total -= amount
    def check_balance(self):
        return self.total
    

person1 = Bank(total=10)

person1.add_money(100)
person1.withdraw_money(50)
# person1.withdraw_money(79) # Error
print(person1.check_balance())
