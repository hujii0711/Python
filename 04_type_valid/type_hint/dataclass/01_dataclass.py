"""
기본: @dataclass는 런타임에 타입을 검사하지 않음
타입 힌트는 힌트일 뿐이라 잘못된 타입을 넣어도 에러가 나지 않습니다.
"""

from dataclasses import dataclass


@dataclass
class User:
    name: str
    age: int


u = User(name=123, age="스물다섯")  # 에러 없이 생성됨
print(u)  # User(name=123, age='스물다섯')
