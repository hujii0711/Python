"""
자동 타입 변환과 검증
"""

from pydantic import BaseModel


class User(BaseModel):
    name: str
    age: int
    email: str | None = None  # 선택 필드 (기본값 None)


# 자동 타입 변환과 검증
u = User(name="영희", age="30")  # "30" -> 30 자동 변환
print(u.age, type(u.age))  # 30 <class 'int'>

User(name="민수", age="abc")
# ValidationError: age - Input should be a valid integer,
#                  unable to parse string as an integer
