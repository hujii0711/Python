"""
`__repr__`는 파이썬의 매직 메서드(Special Method) 중 하나로, 객체를 개발자 관점에서 표현하는 문자열을 반환하는 메서드입니다.
- `__repr__` → 개발자가 객체를 이해하고 디버깅하기 위한 표현
- `__str__`이 없으면 `print(obj)`도 `__repr__`을 사용합니다.
"""


class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def __repr__(self):
        return f"Person(name={self.name!r}, age={self.age})"

    # {self.name!r}의 의미: `!r`은 `repr()` 함수를 호출하여 문자열을 반환하도록 지정하는 포맷 코드입니다.


a = Person("Kim", 30)
print(a)  # __repr__ 없을때 <__main__.Person object at 0x104d3c610>

p = Person("Kim", 30)
print(p)
