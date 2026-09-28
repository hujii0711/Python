"""
딕셔너리 구조 정의
"""

from typing import TypedDict


class User(TypedDict):
    name: str
    age: int
    email: str


user: User = {"name": "Alice", "age": 30, "email": "alice@example.com"}
