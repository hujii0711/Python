"""
사실 람다는 `add = lambda a, b: a + b`처럼 변수에 저장해서 쓰는 경우는 드물고,
주로 다른 함수의 인자로 즉석에서 넘길 때 진가를 발휘해요.
대표적으로 `map()`, `filter()`, `sorted()`와 함께 자주 쓰입니다.
"""

# `sorted()`와 함께 — 정렬 기준 지정
students = [("철수", 85), ("영희", 92), ("민수", 78)]

# 점수(두 번째 값) 기준으로 정렬
result = sorted(students, key=lambda x: x[1])
print(result)  # [('민수', 78), ('철수', 85), ('영희', 92)]

# ---
# `map()`과 함께 — 리스트의 모든 원소에 함수 적용
numbers = [1, 2, 3, 4, 5]

# 모든 원소를 제곱하기
squared = list(map(lambda x: x**2, numbers))
# squared = [x**2 for x in numbers]
print(squared)

# ---
# `filter()`와 함께 — 조건에 맞는 값만 골라내기
numbers2 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# 짝수만 골라내기
evens = list(filter(lambda x: x % 2 == 0, numbers2))
print(evens)

# ---
# 조건 표현식(삼항연산자)은 가능
calc = lambda x: "양수" if x > 0 else "음수 또는 0"
print(calc(5))  # 양수
print(calc(-3))  # 음수 또는 0
