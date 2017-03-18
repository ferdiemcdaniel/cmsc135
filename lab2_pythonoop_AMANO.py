class SavingsAccount:
    def __init__(self,balance = 0, interest = 0.05):
        self.balance = balance
        self.interest = interest

    def deposit(self, amount):
        self.balance += amount
        return self.balance
    
    def withdraw(self, amount):
        self.balance -= amount
        return self.balance

    def compute_interest():
        return self.balance * self.interest

    __compute_interest = compute_interest

    def add_interest():
        self.balance += __compute_interest()

    @staticmethod
    def bank_information():
        return "Banko ni Juan";


a = SavingsAccount()
print a.balance
print a.interest
print a.deposit(100)
print SavingsAccount.bank_information()
