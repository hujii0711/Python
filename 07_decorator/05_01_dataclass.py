"""
`@dataclass`는 Python 3.7+에서 도입된 데코레이터로, 데이터를 저장하는 클래스를 간결하게 작성할 수 있게 해줍니다.
`__init__`, `__repr__`, `__eq__` 등의 특수 메서드를 자동으로 생성해줍니다.
"""

from dataclasses import dataclass


# 일반 클래스 (boilerplate 많음)
class PersonOld:
    def __init__(self, name: str, age: int, email: str):
        self.name = name
        self.age = age
        self.email = email

    def __repr__(self):
        return f"Person(name={self.name}, age={self.age}, email={self.email})"

    def __eq__(self, other):
        return self.name == other.name and self.age == other.age


# @dataclass 사용 (훨씬 간결!)
@dataclass
class Person:
    name: str
    age: int
    email: str


p1 = Person("Alice", 30, "alice@example.com")
p2 = Person("Alice", 30, "alice@example.com")

print(p1)  # Person(name='Alice', age=30, email='alice@example.com')
print(p1 == p2)  # True (자동 생성된 __eq__)
