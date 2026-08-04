#!/usr/bin/python
import numpy as np

# Represent a user
class User:
    def __init__(self, username, pin, balance):
        self.username = username  # Public attribute
        self.__pin = pin  # Private attribute
        self.__balance = balance  # Private attribute
        self.transaction_history = []

    def authenticate(self, input_pin):
        """Check if the entered PIN matches the user's PIN."""
        return self.__pin == input_pin

    def change_pin(self, new_pin):
        """Change the user's PIN securely."""
        self.__pin = new_pin
        print("NEW PIN SAVED.")

    def get_balance(self):
        """Getter for the user's balance."""
        return self.__balance

    def set_balance(self, amount):
        """Setter for the user's balance."""
        self.__balance = amount

    def add_transaction(self, transaction):
        """Add a transaction to the user's history."""
        self.transaction_history = np.append(self.transaction_history, transaction)


# Transaction logic
class Transaction:
    MIN_AMOUNT = 500  # Minimum amount
    RECEIPT_FEE = 3  # Fee for printing a receipt

    @staticmethod
    def validate_amount(amount):
        """Validate if the transaction amount is allowed."""
        if amount < Transaction.MIN_AMOUNT:
            print(f"MINIMUM AMOUNT IS {Transaction.MIN_AMOUNT} TAKA.")
            return False
        if amount % 500 != 0:
            print("AMOUNT MUST BE A MULTIPLE OF 500 TAKA.")
            return False
        return True


# Subclasses for specific transactions
class Withdrawal(Transaction):
    MAX_WITHDRAWAL_PER_TRANSACTION = 20000 
    MAX_WITHDRAWAL_PER_DAY = 80000  

    def __init__(self, balance_manager):
        self.balance_manager = balance_manager
        self.daily_withdrawal_total = 0  

    def execute(self, amount):
        """Perform a withdrawal after validating the amount."""
        # Check maximum withdrawal per transaction
        if amount > Withdrawal.MAX_WITHDRAWAL_PER_TRANSACTION:
            print(f"YOU CAN ONLY WITHDRAW A MAXIMUM OF {Withdrawal.MAX_WITHDRAWAL_PER_TRANSACTION} TAKA PER TRANSACTION.")
            return

        # Check daily withdrawal limit
        if self.daily_withdrawal_total + amount > Withdrawal.MAX_WITHDRAWAL_PER_DAY:
            print(f"DAILY LIMIT REACHED. YOU CAN ONLY WITHDRAW UP TO {Withdrawal.MAX_WITHDRAWAL_PER_DAY} TAKA IN A DAY.")
            return

        if not self.validate_amount(amount):
            return

        if self.balance_manager.deduct(amount, "Withdrawal"):
            self.daily_withdrawal_total += amount
            print(f"WITHDRAWAL OF {amount} TAKA SUCCESSFUL.")

            try:
                receipt = input("WOULD YOU LIKE A RECEIPT FOR AN EXTRA 3 TAKA? (Y/N): ").strip().lower()
                if receipt == 'y':
                    if self.balance_manager.deduct(Transaction.RECEIPT_FEE, "Receipt Fee"):
                        print("RECEIPT PRINTED. EXTRA 3 TAKA DEDUCTED.")
                print(f"NEW BALANCE: {self.balance_manager.user.get_balance()} TAKA.")
            except Exception as e:
                print("AN ERROR OCCURRED WHILE PROCESSING YOUR RECEIPT REQUEST.", e)



class Deposit(Transaction):
    def __init__(self, balance_manager):
        self.balance_manager = balance_manager

    def execute(self, amount):
        """Handle deposits by validating the amount and adding it to the balance."""
        if self.validate_amount(amount):
            self.balance_manager.add(amount, "Deposit")
            print(f"DEPOSIT SUCCESSFUL. NEW BALANCE: {self.balance_manager.user.get_balance()} TAKA.")


class TopUp(Transaction):
    def __init__(self, balance_manager):
        self.balance_manager = balance_manager

    def execute(self, phone_number, amount):
        """Perform a mobile top-up after validating the amount and deducting it."""
        if self.validate_amount(amount) and self.balance_manager.deduct(amount, f"Mobile Top-up ({phone_number})"):
            print(f"MOBILE TOP-UP OF {amount} TAKA TO {phone_number} SUCCESSFUL. NEW BALANCE: {self.balance_manager.user.get_balance()} TAKA.")




# Balance-related operations
class BalanceManager:
    def __init__(self, user):
        self.user = user

    def get_balance(self):
        """Display the user's current balance."""
        print(f"{self.user.username}, YOU HAVE {self.user.get_balance()} TAKA IN YOUR ACCOUNT.")

    def deduct(self, amount, description):
        """Deduct the specified amount from the user's balance."""
        if amount > self.user.get_balance():
            print("INSUFFICIENT BALANCE.")
            return False
        self.user.set_balance(self.user.get_balance() - amount)
        self.user.add_transaction(f"-{amount} TAKA: {description}")
        return True

    def add(self, amount, description):
        """Add the specified amount to the user's balance."""
        self.user.set_balance(self.user.get_balance() + amount)
        self.user.add_transaction(f"+{amount} TAKA: {description}")

# Customer Support Class
class CustomerSupport:
    def __init__(self):
        self.support_tickets = []  # List to store support tickets

    def log_issue(self, username, issue):
        """Log a customer issue."""
        ticket_id = len(self.support_tickets) + 1
        self.support_tickets.append({"ticket_id": ticket_id, "username": username, "issue": issue, "status": "Open"})
        print(f"ISSUE LOGGED SUCCESSFULLY. YOUR TICKET ID IS {ticket_id}. OUR TEAM WILL REACH OUT SOON.")

    def view_tickets(self, username):
        """View all tickets for a specific user."""
        print(f"\nTICKETS FOR USER: {username}")
        user_tickets = [ticket for ticket in self.support_tickets if ticket["username"] == username]
        if user_tickets:
            for ticket in user_tickets:
                print(f"Ticket ID: {ticket['ticket_id']}, Issue: {ticket['issue']}, Status: {ticket['status']}")
        else:
            print("NO TICKETS FOUND.")

    def resolve_ticket(self, ticket_id):
        """Mark a ticket as resolved."""
        for ticket in self.support_tickets:
            if ticket["ticket_id"] == ticket_id:
                ticket["status"] = "Resolved"
                print(f"TICKET {ticket_id} MARKED AS RESOLVED.")
                return
        print("TICKET NOT FOUND.")


# All account-related operations
class Account:
    def __init__(self, user):
        self.user = user
        self.balance_manager = BalanceManager(user)
        self.withdrawal = Withdrawal(self.balance_manager)

    def deposit(self, amount):
        """Handle deposits by validating the amount and adding it to the balance."""
        if Transaction.validate_amount(amount):
            self.balance_manager.add(amount, "Deposit")
            print(f"DEPOSIT SUCCESSFUL. NEW BALANCE: {self.user.get_balance()} TAKA.")

    def pay_bill(self, bill_type, amount):
        """Pay bills after validating the amount and deducting it from the balance."""
        if Transaction.validate_amount(amount) and self.balance_manager.deduct(amount, f"{bill_type.capitalize()} Bill Payment"):
            print(f"{bill_type.capitalize()} BILL PAYMENT OF {amount} TAKA SUCCESSFUL. NEW BALANCE: {self.user.get_balance()} TAKA.")

    def mobile_topup(self, phone_number, amount):
        """Perform a mobile top-up after validating the amount and deducting it."""
        if Transaction.validate_amount(amount) and self.balance_manager.deduct(amount, f"Mobile Top-up ({phone_number})"):
            print(f"MOBILE TOP-UP OF {amount} TAKA TO {phone_number} SUCCESSFUL. NEW BALANCE: {self.user.get_balance()} TAKA.")

    def fund_transfer(self, recipient_user, amount):
        """Perform a fund transfer and update both balances."""
        if Transaction.validate_amount(amount):
            if self.balance_manager.deduct(amount, f"Transfer to {recipient_user.username}"):
                recipient_user.set_balance(recipient_user.get_balance() + amount)
                recipient_user.add_transaction(f"+{amount} TAKA: Transfer from {self.user.username}")
                print(f"FUND TRANSFER OF {amount} TAKA TO {recipient_user.username} SUCCESSFUL.")
                print(f"NEW BALANCE: {self.user.get_balance()} TAKA.")

    def show_mini_statement(self):
        """
        Display all transaction history for the user in the form of a mini-statement.
        """
        print("\n===== Mini Statement =====")
        
        # Explicitly handle transaction history
        transaction_history = list(self.user.transaction_history)  

        if transaction_history:  
            print("\nRecent Transactions:")

            # Display each transaction
            for index, transaction in enumerate(transaction_history, start=1):
                print(f"{index}. {transaction}")
            
            print("\n===========================")
        else:
            print("No transactions available.")
            print("\n===========================")


class Security:
    MAX_ATTEMPTS = 3  # Maximum allowed PIN attempts

    def __init__(self):
        self.locked = False  # Flag to indicate if the account is locked
        self.attempts = 0  # Track failed attempts

    def validate_pin(self, input_pin, actual_pin):
        """Validate PIN and lock the account after too many failed attempts."""
        if self.locked:
            print("ACCOUNT IS LOCKED. PLEASE CONTACT CUSTOMER SUPPORT.")
            return False

        if input_pin == actual_pin:
            self.attempts = 0  # Reset attempts on success
            return True
        else:
            self.attempts += 1
            if self.attempts >= self.MAX_ATTEMPTS:
                self.locked = True
                print("TOO MANY FAILED ATTEMPTS. ACCOUNT LOCKED.")
            else:
                print(f"INVALID PIN. {self.MAX_ATTEMPTS - self.attempts} ATTEMPTS REMAINING.")
            return False


# Subclass for changing PIN
class ChangePin(Account, Security):
    def __init__(self, user):
        Account.__init__(self, user)
        Security.__init__(self)

    def execute(self):
        """Handle the process of securely changing the PIN."""
        print("\nCHANGE PIN PROCESS")
        for _ in range(3):  # Allow up to 3 attempts for PIN validation
            input_pin = input("PLEASE ENTER YOUR CURRENT PIN: ")
            if self.user.authenticate(input_pin):
                new_pin = input("ENTER YOUR NEW PIN: ").strip()
                confirm_pin = input("CONFIRM YOUR NEW PIN: ").strip()

                if new_pin == confirm_pin:
                    self.user.change_pin(new_pin)
                    print("PIN CHANGED SUCCESSFULLY.")
                    break
                else:
                    print("NEW PIN AND CONFIRMATION PIN DO NOT MATCH. TRY AGAIN.")
            else:
                print("INVALID CURRENT PIN.")
        else:
            print("TOO MANY FAILED ATTEMPTS. EXITING PIN CHANGE PROCESS.")


# Manage the ATM system and user interactions
class ATM:
    def __init__(self):
        self.users = {
            'shehab': User('shehab', '1722', 50000),
            'ritu': User('ritu', '1740', 60000),
            'saba': User('saba', '1631', 65000),
        }
        self.current_user = None
        self.account = None
        self.customer_support = CustomerSupport()  # Add customer support instance

    def start(self):
        self.show_title()
        self.authenticate_user()
        self.main_menu()

    def show_title(self):
        """Display the ATM title."""
        print("\n")
        print("=" * 50)
        print("      SRS ATM powered by Safekey Guardians")
        print("=" * 50)
        print("\n")

    def authenticate_user(self):
        """Authenticate the user by verifying username and PIN."""
        attempts = 0
        while attempts < 3:
            username = input("\nENTER USER NAME: ").lower()
            if username in self.users:
                self.current_user = self.users[username]
                if self.check_pin():
                    print("LOGIN SUCCESSFUL.")
                    self.account = Account(self.current_user)
                    break
            else:
                print("INVALID USERNAME.")
                attempts += 1
        else:
            print("3 UNSUCCESSFUL ATTEMPTS. EXITING. YOUR CARD IS LOCKED.")
            exit()

    def check_pin(self):
        """Verify the user's PIN."""
        for _ in range(3):
            pin = input("PLEASE ENTER PIN: ")
            if self.current_user.authenticate(pin):
                return True
            print("INVALID PIN.")
        return False

    def main_menu(self):
        """Display the main menu and handle user options."""
        while True:
            print("\nSELECT OPTION: \nBalance Inquiry (B) \nMini Statement (M) \nWithdraw (W) \nDeposit (D) \nChange PIN (P) \nBill Pay (L) \nTop-up (T) \nFund Transfer (F) \nCustomer Support (C) \nQuit (Q)\n")
            choice = input("SELECT AN OPTION: ").strip().lower()

            if choice == 'b':
                self.account.balance_manager.get_balance()
            elif choice == 'm':
                self.account.show_mini_statement()
            elif choice == 'w':
                self.handle_withdraw()
            elif choice == 'd':
                self.handle_deposit()
            elif choice == 'l':
                self.handle_bill_payment()
            elif choice == 't':
                self.handle_top_up()
            elif choice == 'f':
                self.handle_fund_transfer()
            elif choice == 'c':
                self.handle_customer_support()
            elif choice == 'p':
                self.handle_pin_change()
            elif choice == 'q':
                print("THANK YOU FOR USING SRS ATM. HAVE A GREAT DAY!")
                break
            else:
                print("INVALID OPTION. PLEASE TRY AGAIN.")

    def handle_withdraw(self):
        try:
            amount = int(input("ENTER WITHDRAWAL AMOUNT: "))
            self.account.withdrawal.execute(amount)  
        except ValueError:
            print("INVALID AMOUNT. PLEASE ENTER A NUMBER.")


    def handle_deposit(self):
        try:
            amount = int(input("ENTER DEPOSIT AMOUNT: "))
            self.account.deposit(amount)
        except ValueError:
            print("INVALID AMOUNT. PLEASE ENTER A NUMBER.")

    def handle_bill_payment(self):
        """Handle bill payment options."""
        try:
            bill_types = {
                1: "Electricity",
                2: "Water",
                3: "Internet",
                4: "Gas",
                5: "Telephone",
                6: "TV",
                7: "Others"
            }

            print("\nBILL TYPES:")
            for key, value in bill_types.items():
                print(f"{key}. {value}")

            choice = int(input("SELECT BILL TYPE (1-7): "))
            if choice in bill_types:
                if choice == 7:  # If the user selects "Others"
                    bill_type = input("ENTER THE NAME OF THE BILL TYPE: ").strip().capitalize()
                else:
                    bill_type = bill_types[choice]

                amount = int(input(f"ENTER AMOUNT FOR {bill_type.upper()} BILL: "))
                self.account.pay_bill(bill_type, amount)
            else:
                print("INVALID BILL TYPE SELECTED.")
        except ValueError:
            print("INVALID INPUT. PLEASE ENTER A VALID NUMBER.")

    def handle_top_up(self):
        try:
            phone_number = input("ENTER PHONE NUMBER: ")
            amount = int(input(f"ENTER TOP-UP AMOUNT FOR {phone_number}: "))
            self.account.mobile_topup(phone_number, amount)
        except ValueError:
            print("INVALID AMOUNT. PLEASE ENTER A NUMBER.")

    def handle_fund_transfer(self):
        recipient_username = input("ENTER RECIPIENT'S USERNAME: ").strip().lower()
        if recipient_username in self.users and recipient_username != self.current_user.username:
            try:
                amount = int(input(f"ENTER AMOUNT TO TRANSFER TO {recipient_username}: "))
                recipient_user = self.users[recipient_username]
                self.account.fund_transfer(recipient_user, amount)
            except ValueError:
                print("INVALID AMOUNT. PLEASE ENTER A NUMBER.")
        else:
            print("INVALID RECIPIENT USERNAME.")

    def handle_pin_change(self):
        change_pin = ChangePin(self.current_user) 
        change_pin.execute()


    def handle_customer_support(self):
        """Handle customer support options."""
        print("\nCUSTOMER SUPPORT OPTIONS:")
        print("1. Log a General Issue")
        print("2. Card Lock")
        print("3. Withdraw Problem")
        print("4. Deposit Problem")
        print("5. Change PIN Issue")
        print("6. Bill Payment Issue")
        print("7. Top-up Issue")
        print("8. Fund Transfer Issue")
        print("9. Mini Statement Issue")
        print("10. View My Tickets")
        print("11. Resolve a Ticket")
        print("12. Back to Main Menu\n")

        try:
            choice = int(input("SELECT AN OPTION: "))
            if choice == 1:
                issue = input("DESCRIBE YOUR ISSUE: ")
                self.customer_support.log_issue(self.current_user.username, issue)
            elif choice == 2:
                self.customer_support.log_issue(self.current_user.username, "Card Lock Issue")
                print("CARD LOCK ISSUE LOGGED SUCCESSFULLY.")
            elif choice == 3:
                self.customer_support.log_issue(self.current_user.username, "Withdrawal Problem")
                print("WITHDRAWAL PROBLEM LOGGED SUCCESSFULLY.")
            elif choice == 4:
                self.customer_support.log_issue(self.current_user.username, "Deposit Problem")
                print("DEPOSIT PROBLEM LOGGED SUCCESSFULLY.")
            elif choice == 5:
                self.customer_support.log_issue(self.current_user.username, "Change PIN Issue")
                print("CHANGE PIN ISSUE LOGGED SUCCESSFULLY.")
            elif choice == 6:
                self.customer_support.log_issue(self.current_user.username, "Bill Payment Issue")
                print("BILL PAYMENT ISSUE LOGGED SUCCESSFULLY.")
            elif choice == 7:
                self.customer_support.log_issue(self.current_user.username, "Top-up Issue")
                print("TOP-UP ISSUE LOGGED SUCCESSFULLY.")
            elif choice == 8:
                self.customer_support.log_issue(self.current_user.username, "Fund Transfer Issue")
                print("FUND TRANSFER ISSUE LOGGED SUCCESSFULLY.")
            elif choice == 9:
                self.customer_support.log_issue(self.current_user.username, "Mini Statement Issue")
                print("MINI STATEMENT ISSUE LOGGED SUCCESSFULLY.")
            elif choice == 10:
                self.customer_support.view_tickets(self.current_user.username)
            elif choice == 11:
                try:
                    ticket_id = int(input("ENTER TICKET ID TO RESOLVE: "))
                    self.customer_support.resolve_ticket(ticket_id)
                except ValueError:
                    print("INVALID TICKET ID. PLEASE TRY AGAIN.")
            elif choice == 12:
                return
            else:
                print("INVALID OPTION. PLEASE TRY AGAIN.")
        except ValueError:
            print("INVALID INPUT. PLEASE TRY AGAIN.")


# Main execution
if __name__ == "__main__":
    atm = ATM()
    atm.start()
