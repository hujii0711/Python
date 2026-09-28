"""
기본값 인자 (Default arguments)
기본값을 지정해두면 호출 시 생략 가능합니다.
"""


def greet(name, age=20):
    print(f"{name}는 {age}살입니다.")


greet("철수")  # age=20 사용
greet("영희", 25)  # age=25로 덮어씀
