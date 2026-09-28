"""
`max_num` 예제처럼 조건식(삼항 연산자)은 람다 안에서도 쓸 수 있어요.
`a if a > b else b`는 "a가 b보다 크면 a, 아니면 b"라는 뜻입니다.
"""

# 제곱 계산
square = lambda x: x**2
print(square(5))  # 25

# 두 수 중 큰 값 구하기
max_num = lambda a, b: a if a > b else b  # noqa: FURB136
print(max_num(3, 7))  # 7

# 짝수인지 판별
is_even = lambda x: x % 2 == 0
print(is_even(4))  # True
print(is_even(7))  # False

# 매개변수 없는 람다
greet = lambda: "안녕하세요"
print(greet())  # 안녕하세요
