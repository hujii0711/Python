"""
가변 위치 인자(*args) 뒤에 자연스럽게 오는 방법
*args 뒤에 선언된 인자들도 자동으로 키워드 전용 인자가 됩니다.
"""


def calculate_total(*prices, discount=0.0, tax=0.1):
    subtotal = sum(prices)
    total = subtotal * (1 - discount) * (1 + tax)
    return total


# prices는 위치 인자로 여러 개 받고, discount와 tax는 키워드 전용으로 받음
result = calculate_total(1000, 2000, 3000, discount=0.1, tax=0.05)
print(result)
