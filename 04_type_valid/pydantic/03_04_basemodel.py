"""
딕셔너리, JSON으로 변환
"""

from pydantic import BaseModel


class User(BaseModel):
    name: str
    age: int
    email: str | None = None  # 선택 필드 (기본값 None)


user = User(name="철수", age=25)

print(user.model_dump())  # {'name': '철수', 'age': 25, 'email': None}
print(user.model_dump_json())  # {"name":"철수","age":25,"email":null}

# 특정 값 제외
print(user.model_dump(exclude_none=True))  # {'name': '철수', 'age': 25}
print(user.model_dump(include={"name"}))  # {'name': '철수'}
