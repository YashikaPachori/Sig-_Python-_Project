import json
import os
import pandas as pd
from datetime import datetime
import getpass
import msvcrt  # This module is only available on Windows

def input_password(prompt='Password: '):
    """Input password with an option to toggle visibility."""
    password = ''
    print(prompt, end='', flush=True)
    while True:
        char = msvcrt.getch()
        if char in (b'\r', b'\n'):
            print()  # Move to the next line after Enter
            break
        elif char == b'\x08':  # Handle backspace
            if password:
                password = password[:-1]
                print('\b \b', end='', flush=True)  # Erase the last character
        else:
            password += char.decode()  # Add the character to the password
            print('*', end='', flush=True)  # Print asterisk for each character
    return password

class FinancialRecord:
    """Class to represent a financial record."""
    
    def __init__(self, description, amount, category, record_type, date=None):
        self.description = description
        self.amount = amount
        self.category = category
        self.record_type = record_type  # 'income' or 'expense'
        self.date = date or datetime.now().strftime('%Y-%m-%d')

    def to_dict(self):
        """Convert the financial record to a dictionary."""
        return {
            'description': self.description,
            'amount': self.amount,
            'category': self.category,
            'record_type': self.record_type,
            'date': self.date
        }

class User:
    """Class to represent a user."""
    
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def to_dict(self):
        """Convert user data to a dictionary."""
        return {
            'username': self.username,
            'password': self.password
        }

class FinanceManager:
    """Class to manage financial records."""
    
    def __init__(self, users_file='users.json', finance_file='finance.json'):
        self.users_file = users_file
        self.finance_file = finance_file
        self.users = self.load_users()
        self.current_user = None
        self.load_financial_records()

    def load_users(self):
        """Load users from a JSON file."""
        if os.path.exists(self.users_file):
            with open(self.users_file, 'r') as file:
                users_data = json.load(file)
                users = {user['username']: User(user['username'], user['password']) for user in users_data}
                return users
        return {}

    def save_users(self):
        """Save users to a JSON file."""
        with open(self.users_file, 'w') as file:
            json.dump([user.to_dict() for user in self.users.values()], file)

    def load_financial_records(self):
        """Load financial records from a JSON file."""
        if os.path.exists(self.finance_file) and os.path.getsize(self.finance_file) > 0:
            with open(self.finance_file, 'r') as file:
                try:
                    records_data = json.load(file)
                    self.financial_records = {}
                    for record in records_data:
                        username = record['username']
                        financial_record = FinancialRecord(
                            description=record['description'],
                            amount=record['amount'],
                            category=record['category'],
                            record_type=record['record_type'],
                            date=record.get('date')
                        )
                        if username not in self.financial_records:
                            self.financial_records[username] = []
                        self.financial_records[username].append(financial_record)
                except json.JSONDecodeError:
                    print("Warning: The finance file is corrupted or invalid. Starting with an empty record set.")
                    self.financial_records = {}
        else:
            self.financial_records = {}

    def save_financial_records(self):
        """Save financial records to a JSON file."""
        records_to_save = []
        for username, records in self.financial_records.items():
            for record in records:
                records_to_save.append({
                    'username': username,
                    **record.to_dict()
                })
        with open(self.finance_file, 'w') as file:
            json.dump(records_to_save, file)

    def register_user(self, username, password):
        """Register a new user."""
        if username in self.users:
            print("Sorry! User already exists.")
            return False
        self.users[username] = User(username, password)
        self.save_users()
        print("User registered successfully.")
        return True

    def authenticate_user(self, username, password):
        """Authenticate a user."""
        if username in self.users and self.users[username].password == password:
            self.current_user = self.users[username]
            print("Congrats! Authentication successful.")
            return True
        print("Invalid username or password. Try Again")
        return False

    def add_record(self, description, amount, category, record_type):
        """Add a financial record."""
        if self.current_user is None:
            print("Please log in to add records.")
            return
        record = FinancialRecord(description, amount, category, record_type)
        if self.current_user.username not in self.financial_records:
            self.financial_records[self.current_user.username] = []
        self.financial_records[self.current_user.username].append(record)
        self.save_financial_records()
        print("Record added successfully!!!.")

    def delete_record(self, record_index):
        """Delete a financial record by index."""
        if self.current_user is None or record_index < 0 or record_index >= len(self.financial_records.get(self.current_user.username, [])):
            print("Invalid record index. Try Again!")
            return
        del self.financial_records[self.current_user.username][record_index]
        self.save_financial_records()
        print("Record deleted successfully!!!")

    def update_record(self, record_index, description=None, amount=None, category=None, record_type=None):
        """Update a financial record."""
        if self.current_user is None or record_index < 0 or record_index >= len(self.financial_records.get(self.current_user.username, [])):
            print("Invalid record index.")
            return
        record = self.financial_records[self.current_user.username][record_index]
        if description is not None:
            record.description = description
        if amount is not None:
            record.amount = amount
        if category is not None:
            record.category = category
        if record_type is not None:
            record.record_type = record_type
        self.save_financial_records()
        print("Congrats! Record updated successfully.")

    def display_records(self):
        """Display all financial records for the current user."""
        if self.current_user is None:
            print("Please log in to view your records.")
            return
        if self.current_user.username not in self.financial_records or not self.financial_records[self.current_user.username]:
            print("No records found at this time.")
            return

        print("\nHere are Your Financial Records:")
        for index, record in enumerate(self.financial_records[self.current_user.username]):
            print(f"{index}. {record.description} | Amount: {record.amount} | Category: {record.category} | Type: {record.record_type} | Date: {record.date}")

    def calculate_totals(self):
        """Calculate total income and total expenses."""
        if self.current_user is None:
            print("Please log in to calculate total income and expense.")
            return None, None

        total_income = sum(record.amount for record in self.financial_records.get(self.current_user.username, []) if record.record_type == 'income')
        total_expenses = sum(record.amount for record in self.financial_records.get(self.current_user.username, []) if record.record_type == 'expense')

        return total_income, total_expenses

    def generate_report(self, period='monthly'):
        """Generate financial report."""
        if self.current_user is None:
            print("Please log in to generate reports.")
            return
        if not self.financial_records.get(self.current_user.username):
            print("No records available for generating reports.")
            return
        
        df = pd.DataFrame([record.to_dict() for record in self.financial_records[self.current_user.username]])
        df['date'] = pd.to_datetime(df['date'])  # Ensure date is in datetime format

        if period == 'monthly':
            report = df.groupby([df['date'].dt.to_period('M'), 'record_type', 'category'])['amount'].sum().reset_index()
        elif period == 'weekly':
            report = df.groupby([df['date'].dt.to_period('W'), 'record_type', 'category'])['amount'].sum().reset_index()
        else:
            print("Invalid period specified.")
            return None
        
        print(report)
        return report

    def calculate_savings(self):
        """Calculate savings."""
        if self.current_user is None:
            print("Please log in to calculate savings.")
            return
        total_income = sum(record.amount for record in self.financial_records.get(self.current_user.username, []) if record.record_type == 'income')
        total_expenses = sum(record.amount for record in self.financial_records.get(self.current_user.username, []) if record.record_type == 'expense')
        savings = total_income - total_expenses
        return savings

    def view_spending_distribution(self):
        """View spending distribution by category."""
        if self.current_user is None:
            print("Please log in to view spending distribution.")
            return
        if not self.financial_records.get(self.current_user.username):
            print("No records available to calculate spending distribution.")
            return

        df = pd.DataFrame([record.to_dict() for record in self.financial_records[self.current_user.username]])
        df['date'] = pd.to_datetime(df['date'])

        # Filter for expenses only
        expense_df = df[df['record_type'] == 'expense']

        if expense_df.empty:
            print("No expenses recorded.")
            return

        # Group by category and sum the amounts
        spending_distribution = expense_df.groupby('category')['amount'].sum().reset_index()

        # Print the spending distribution
        print("\nSpending Distribution by Category:")
        print(spending_distribution)

if __name__ == "__main__":
    manager = FinanceManager()

    while True:
        print("\n1. Register\n2. Login\n3. Add Record\n4. Delete Record\n5. Update Record\n6. Generate Report\n7. Calculate Savings\n8. View Spending Distribution\n9. Total income and expense\n10. Exit")
        choice = input("Choose an option: ")

        if choice == '1':
            print("******USER REGISTRATION******")
            username = input("Enter username: ")
            password = input_password("Enter password: ")
            manager.register_user(username, password)

        elif choice == '2':
            print("******USER LOGIN******")
            username = input("Enter username: ")
            password = input_password("Enter password: ")
            if manager.authenticate_user(username, password):
                print(f"WELCOME {manager.current_user.username}, TO YOUR PERSONAL FINANCE MANAGER!")

        elif choice == '3':
            print("******ADD RECORDS******")
            if manager.current_user:
                manager.display_records()  # Display records before adding
                description = input("Enter description: ")
                try:
                    amount = float(input("Enter amount: "))
                except ValueError:
                    print("Invalid amount. Please enter a numeric value.")
                    continue
                category = input("Enter category: ")
                record_type = input("Enter type (income/expense): ")
                manager.add_record(description, amount, category, record_type)
            else:
                print("Please log in first.")

        elif choice == '4':
            print("******DELETE RECORDS******")
            if manager.current_user:
                manager.display_records()  # Display records before deleting
                try:
                    record_index = int(input("Enter record index to delete: "))
                    manager.delete_record(record_index)
                except ValueError:
                    print("Invalid index. Please enter a numeric value.")
            else:
                print("Please log in first.")

        elif choice == '5':
            print("******UPDATE RECORDS******")
            if manager.current_user:
                manager.display_records()  # Display records before updating
                try:
                    record_index = int(input("Enter record index to update: "))
                    description = input("Enter new description (or leave blank): ")
                    amount = input("Enter new amount (or leave blank): ")
                    category = input("Enter new category (or leave blank): ")
                    record_type = input("Enter new type (income/expense or leave blank): ")

                    manager.update_record(
                        record_index,
                        description or None,
                        float(amount) if amount else None,
                        category or None,
                        record_type or None
                    )
                except ValueError:
                    print("Invalid input. Please enter numeric values for amount and valid index.")
            else:
                print("Please log in first.")

        elif choice == '6':
            print("******GENERATE REPORT******")
            period = input("Enter report period (monthly/weekly): ")
            manager.generate_report(period)

        elif choice == '7':
            savings = manager.calculate_savings()
            if savings is not None:
                print(f"Total Savings: {savings}")

        elif choice == '8':
            print("************")
            manager.view_spending_distribution()  # Call the new method
            
        elif choice == '9':
            total_income, total_expenses = manager.calculate_totals()
            if total_income is not None and total_expenses is not None:
                print(f"Total Income: {total_income}")
                print(f"Total Expenses: {total_expenses}")

        elif choice == '10':
            print("Exiting...")
            break

        else:
            print("Invalid choice, please try again.")
