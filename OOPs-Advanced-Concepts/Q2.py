# Employee Management System for Multinational Company

from datetime import datetime, date, timedelta
import re

class Employee:
    # Class variables - shared across all instances
    company_name = "GlobalTech Solutions"
    total_employees = 0
    departments = {}  # Track employee count per department
    tax_rates = {     # Tax rates by country
        "USA": 0.25,
        "UK": 0.20,
        "India": 0.30,
        "Germany": 0.35,
        "Canada": 0.22
    }
    next_employee_id = 1
    approved_departments = ["Engineering", "Marketing", "Sales", "HR", "Finance", "Operations"]
    
    def __init__(self, name, department, base_salary, country, email):
        # Validate inputs using static methods
        if not self.validate_email(email):
            raise ValueError("Invalid email format")
        if not self.is_valid_department(department):
            raise ValueError(f"Invalid department. Must be one of: {self.approved_departments}")
        if not isinstance(base_salary, (int, float)) or base_salary <= 0:
            raise ValueError("Base salary must be a positive number")
        if country not in self.tax_rates:
            raise ValueError(f"Country not supported. Available: {list(self.tax_rates.keys())}")
        
        # Generate unique employee_id
        self.employee_id = self.generate_employee_id()
        
        # Set instance variables
        self.name = name
        self.department = department
        self.base_salary = base_salary
        self.country = country
        self.email = email
        self.hire_date = date.today()
        self.performance_ratings = []
        
        # Update class variables
        Employee.total_employees += 1
        if department in Employee.departments:
            Employee.departments[department] += 1
        else:
            Employee.departments[department] = 1
    
    # === STATIC METHODS ===
    # Static methods don't access instance or class data
    
    @staticmethod
    def validate_email(email):
        # Check basic format and use regex for validation
        if not isinstance(email, str) or not email:
            return False
        
        # Email regex pattern
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(pattern, email):
            return False
        
        # Additional checks for common domains
        valid_domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'company.com', 'globaltech.com']
        domain = email.split('@')[1].lower()
        
        # Allow any domain that follows proper format, not just the predefined ones
        return True
    
    @staticmethod
    def calculate_tax(salary, country):
        # Get tax rate from class variable
        if country in Employee.tax_rates:
            tax_rate = Employee.tax_rates[country]
        else:
            # Default tax rate for unknown countries
            tax_rate = 0.25
        
        return salary * tax_rate
    
    @staticmethod
    def is_valid_department(dept):
        # Check if department is in approved list
        return dept in Employee.approved_departments
    
    @staticmethod
    def generate_employee_id():
        # Generate ID in format "EMP-YYYY-XXXX"
        current_year = datetime.now().year
        employee_number = str(Employee.next_employee_id).zfill(4)  # Zero-padded to 4 digits
        Employee.next_employee_id += 1
        
        return f"EMP-{current_year}-{employee_number}"
    
    # === CLASS METHODS ===
    # Class methods work with class variables, take 'cls' as first parameter
    
    @classmethod
    def from_csv_data(cls, csv_line):
        # Create employee from CSV format: "name,dept,salary,country,email"
        try:
            parts = csv_line.strip().split(', ')
            if len(parts) != 5:
                raise ValueError("CSV line must have exactly 5 comma-separated values")
            
            name, department, salary_str, country, email = parts
            salary = float(salary_str)
            
            return cls(name, department, salary, country, email)
        except Exception as e:
            raise ValueError(f"Error parsing CSV data: {e}")
    
    @classmethod
    def get_department_stats(cls):
        # Return department statistics
        stats = {}
        
        for dept, count in cls.departments.items():
            stats[dept] = {"count": count}
        
        stats["total_employees"] = cls.total_employees
        stats["total_departments"] = len(cls.departments)
        
        if cls.total_employees > 0:
            stats["average_per_department"] = cls.total_employees / len(cls.departments) if cls.departments else 0
        
        return stats
    
    @classmethod
    def set_tax_rate(cls, country, rate):
        # Update tax rate for specific country
        if not isinstance(rate, (int, float)):
            raise ValueError("Tax rate must be a number")
        if not (0.0 <= rate <= 1.0):
            raise ValueError("Tax rate must be between 0.0 and 1.0")
        
        cls.tax_rates[country] = rate
    
    @classmethod
    def hire_bulk_employees(cls, employee_list):
        # Process multiple employee hires
        hired_employees = []
        
        for csv_line in employee_list:
            try:
                employee = cls.from_csv_data(csv_line)
                hired_employees.append(employee)
            except Exception as e:
                print(f"Failed to hire employee from line '{csv_line}': {e}")
        
        return hired_employees
    
    # === INSTANCE METHODS ===
    # Instance methods work with individual employee data
    
    def add_performance_rating(self, rating):
        # Add performance rating with validation
        if not isinstance(rating, (int, float)):
            raise ValueError("Rating must be a number")
        if not (1 <= rating <= 5):
            raise ValueError("Rating must be between 1 and 5")
        
        self.performance_ratings.append(rating)
    
    def get_average_performance(self):
        # Calculate average performance
        if not self.performance_ratings:
            return 0.0  # Return 0 if no ratings
        
        return sum(self.performance_ratings) / len(self.performance_ratings)
    
    def calculate_net_salary(self):
        # Calculate salary after taxes
        tax_amount = self.calculate_tax(self.base_salary, self.country)
        return self.base_salary - tax_amount
    
    def get_years_of_service(self):
        # Calculate years from hire_date to now
        current_date = date.today()
        service_days = (current_date - self.hire_date).days
        return round(service_days / 365.25, 2)  # Account for leap years
    
    def is_eligible_for_bonus(self):
        # Check bonus eligibility
        avg_performance = self.get_average_performance()
        years_service = self.get_years_of_service()
        
        return avg_performance > 3.5 and years_service > 1
    
    def __str__(self):
        # String representation
        return f"Employee {self.employee_id}: {self.name} ({self.department}, {self.country})"

# === TESTING SECTION ===
# if __name__ == "__main__":
#     print("Employee Management System")
#     print("=" * 40)
    
#     # Test 1: Creating individual employees
#     print("\n1. Creating individual employees:")
#     emp1 = Employee("John Doe", "Engineering", 75000, "USA", "john.doe@globaltech.com")
#     emp2 = Employee("Jane Smith", "Marketing", 65000, "UK", "jane.smith@globaltech.com")
#     emp3 = Employee("Raj Patel", "Finance", 70000, "India", "raj.patel@globaltech.com")
    
#     print(f"Created: {emp1}")
#     print(f"Created: {emp2}")
#     print(f"Created: {emp3}")
    
#     # Test 2: Static methods
#     print("\n2. Testing static methods:")
#     print(f"Email validation: {Employee.validate_email('test@gmail.com')}")
#     print(f"Department validation: {Employee.is_valid_department('Engineering')}")
#     print(f"Tax calculation: ${Employee.calculate_tax(75000, 'USA'):.2f}")
    
#     # Test 3: Performance ratings
#     print("\n3. Testing performance ratings:")
#     emp1.add_performance_rating(4.5)
#     emp1.add_performance_rating(4.0)
#     emp1.add_performance_rating(3.8)
#     print(f"{emp1.name}'s average performance: {emp1.get_average_performance():.2f}")
    
#     # Test 4: Salary calculations
#     print("\n4. Testing salary calculations:")
#     print(f"{emp1.name}'s gross salary: ${emp1.base_salary:,.2f}")
#     print(f"{emp1.name}'s net salary: ${emp1.calculate_net_salary():,.2f}")
    
#     # Test 5: Bonus eligibility
#     print("\n5. Testing bonus eligibility:")
#     print(f"{emp1.name} eligible for bonus: {emp1.is_eligible_for_bonus()}")
#     print(f"Years of service: {emp1.get_years_of_service()} years")
    
#     # Test 6: Class methods
#     print("\n6. Testing class methods:")
#     print("Department statistics:")
#     stats = Employee.get_department_stats()
#     for key, value in stats.items():
#         print(f"  {key}: {value}")
    
#     # Test 7: CSV bulk hiring
#     print("\n7. Testing bulk hiring from CSV:")
#     csv_data = [
#         "Alice Johnson,HR,60000,Canada,alice@globaltech.com",
#         "Bob Wilson,Sales,55000,USA,bob@globaltech.com",
#         "Carol Brown,Operations,58000,Germany,carol@globaltech.com"
#     ]
    
#     new_employees = Employee.hire_bulk_employees(csv_data)
#     print(f"Hired {len(new_employees)} employees:")
#     for emp in new_employees:
#         print(f"  {emp}")
    
#     # Test 8: Updated statistics
#     print("\n8. Updated company statistics:")
#     final_stats = Employee.get_department_stats()
#     print(f"Total employees: {Employee.total_employees}")
#     print("Department breakdown:")
#     for dept, count in final_stats["department_counts"].items():
#         print(f"  {dept}: {count} employees")
    
#     # Test 9: Tax rate updates
#     print("\n9. Testing tax rate updates:")
#     print(f"Original USA tax rate: {Employee.tax_rates['USA']}")
#     Employee.set_tax_rate("USA", 0.28)
#     print(f"Updated USA tax rate: {Employee.tax_rates['USA']}")
    
#     print("\n" + "=" * 40)
#     print("All tests completed successfully!")



# Test Case 1: Class setup and basic functionality
Employee.company_name = "GlobalTech Solutions"
Employee.tax_rates = {"USA": 0.22, "India": 0.18, "UK": 0.25}
Employee.departments = {"Engineering": 0, "Sales": 0, "HR": 0, "Marketing": 0}

emp1 = Employee("John Smith", "Engineering", 85000, "USA", "john.smith@globaltech.com")
assert emp1.employee_id.startswith("EMP-2025-")
assert Employee.total_employees == 1
assert Employee.departments["Engineering"] == 1

# Test Case 2: Static method validations
assert Employee.validate_email("test@company.com") == True
assert Employee.validate_email("invalid.email") == False
assert Employee.is_valid_department("Engineering") == True
assert Employee.is_valid_department("InvalidDept") == False
assert abs(Employee.calculate_tax(100000, "USA") - 22000) < 0.01


# Test Case 3: Class methods and bulk operations
emp2 = Employee.from_csv_data("Sarah Johnson, Sales, 75000, UK, sarah.j@globaltech.com")
assert emp2.name == "Sarah Johnson"
assert emp2.department == "Sales"
assert Employee.departments["Sales"] == 1

bulk_data = [
    "Mike Wilson, Marketing, 65000, India, mike.w@globaltech.com",
    "Lisa Chen, HR, 70000, USA, lisa.chen@globaltech.com"
]
Employee.hire_bulk_employees(bulk_data)
assert Employee.total_employees == 4
stats = Employee.get_department_stats()
assert stats["Engineering"]["count"] == 1
assert stats["Sales"]["count"] == 1

# Test Case 4: Performance and bonus calculations
emp1.add_performance_rating(4.2)
emp1.add_performance_rating(3.8)
emp1.add_performance_rating(4.5)
assert abs(emp1.get_average_performance() - 4.17) < 0.01

# Simulate employee with 2 years of service
emp1.hire_date = date.today() - timedelta(days=800)
assert emp1.get_years_of_service() >= 2
assert emp1.is_eligible_for_bonus() == True

# Test Case 5: Salary calculations
net_salary = emp1.calculate_net_salary()
expected_net = 85000 - (85000 * 0.22)
assert abs(net_salary - expected_net) < 0.01