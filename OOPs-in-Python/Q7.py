class Account:
    bank_name = "National Bank"
    _total_accounts = 0
    _minimum_balance = 0

    def __init__(self, account_number, account_holder, initial_balance):
        if not account_holder:
            raise ValueError("Account holder name cannot be empty.")
        if initial_balance < 0:
            raise ValueError("Initial balance cannot be negative.")
        if initial_balance < Account._minimum_balance:
            raise ValueError(f"Initial balance must be at least ${Account._minimum_balance}.")

        self._account_number = account_number
        self._account_holder = account_holder
        self._balance = initial_balance
        Account._total_accounts += 1

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("Deposit amount must be positive.")
        self._balance += amount

    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive.")
        if self._balance >= amount:
            self._balance -= amount
            return True
        return False

    def get_balance(self):
        return self._balance

    def __str__(self):
        return f"[{self.__class__.__name__}] {self._account_holder} | Acc#: {self._account_number} | Balance: ${self._balance:.2f}"

    @classmethod
    def get_total_accounts(cls):
        return cls._total_accounts

    @classmethod
    def set_bank_name(cls, name):
        cls.bank_name = name

    @classmethod
    def set_minimum_balance(cls, amount):
        if amount < 0:
            raise ValueError("Minimum balance must be non-negative.")
        cls._minimum_balance = amount


class SavingsAccount(Account):
    def __init__(self, account_number, account_holder, initial_balance, interest_rate):
        super().__init__(account_number, account_holder, initial_balance)
        if interest_rate < 0:
            raise ValueError("Interest rate must be non-negative.")
        self._interest_rate = interest_rate

    def calculate_monthly_interest(self):
        monthly_interest = self._balance * (self._interest_rate / 100) / 12
        return round(monthly_interest, 2)


class CheckingAccount(Account):
    def __init__(self, account_number, account_holder, initial_balance, overdraft_limit):
        super().__init__(account_number, account_holder, initial_balance)
        if overdraft_limit < 0:
            raise ValueError("Overdraft limit must be non-negative.")
        self._overdraft_limit = overdraft_limit

    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive.")
        if self._balance + self._overdraft_limit >= amount:
            self._balance -= amount
            return True
        return False
    



    # Test Case 1: Creating different types of accounts
savings_account = SavingsAccount("SA001", "Alice Johnson", 1000, 2.5)
checking_account = CheckingAccount("CA001", "Bob Smith", 500, 200)
print(f"Savings Account: {savings_account}")
print(f"Checking Account: {checking_account}")

# Test Case 2: Deposit and Withdrawal operations
print(f"Savings balance before: ${savings_account.get_balance()}")
savings_account.deposit(500)
print(f"After depositing $500: ${savings_account.get_balance()}")
withdrawal_result = savings_account.withdraw(200)
print(f"Withdrawal result: {withdrawal_result}")
print(f"Balance after withdrawal: ${savings_account.get_balance()}")

# Test Case 3: Overdraft protection in checking account
print(f"Checking balance: ${checking_account.get_balance()}")
overdraft_result = checking_account.withdraw(600)
print(f"Overdraft withdrawal: {overdraft_result}")
print(f"Balance after overdraft: ${checking_account.get_balance()}")

# Test Case 4: Interest calculation for savings
interest_earned = savings_account.calculate_monthly_interest()
print(f"Monthly interest earned: ${interest_earned}")

# Test Case 5: Class methods and variables
print(f"Total accounts created: {Account.get_total_accounts()}")
print(f"Bank name: {Account.bank_name}")

# Change bank settings using class method
Account.set_bank_name("New National Bank")
Account.set_minimum_balance(100)

# Test Case 6: Account validation
try:
    invalid_account = SavingsAccount("SA002", "", -100, 1.5)
except ValueError as e:
    print(f"Validation error: {e}")