"""
데이터 타입 자체는 아니지만, `for in`문과 결합하여 반복을 만들어내는 특수한 객체들입니다.
1) range
2) enumerate
3) zip
"""

#  **`range()` 함수:** 특정 횟수만큼 반복하거나 연속된 숫자를 만들 때 필수적입니다.
for i in range(3):  # 0, 1, 2
    print(i)

# `enumerate()` 함수: 순회할 때 요소뿐만 아니라 인덱스(몇 번째인지)를 함께 꺼내줍니다.
for idx, name in enumerate(["Kim", "Lee"]):
    print(f"{idx}번: {name}")  # 0번: Kim, 1번: Lee

# `zip()` 함수: 여러 개의 리스트를 엮어서 동시에 하나씩 꺼낼 때 사용합니다.
for fruit, color in zip(["apple", "banana"], ["red", "yellow"]):
    print(f"{fruit}은 {color}")
