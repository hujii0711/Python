"""
- dataclass에서는 자동 생성
"""

from dataclasses import dataclass


@dataclass
class Person:
    name: str
    age: int


p = Person("Kim", 30)

print(p)
