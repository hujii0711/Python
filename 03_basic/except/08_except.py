"""
커스텀 예외
"""


class InsufficientFundsError(Exception):
    def __init__(self, balance, amount):
        super().__init__(f"잔액 부족: 잔액 {balance}, 출금 요청 {amount}")
        self.balance = balance
        self.amount = amount


def withdraw(balance, amount):
    if amount > balance:
        raise InsufficientFundsError(balance, amount)
    return balance - amount


try:
    withdraw(1000, 5000)
except InsufficientFundsError as e:
    print(e)  # 잔액 부족: 잔액 1000, 출금 요청 5000
    print(e.balance)  # 1000
