"""
@dataclass와 달리 BaseModel은 키워드 인자로만 생성합니다. User("철수", 25)처럼 위치 인자로 넣으면 에러가 납니다.
"""

from pydantic import BaseModel


class User(BaseModel):
    name: str
    age: int
    email: str | None = None  # 선택 필드 (기본값 None)


user = User(name="철수", age=25)
print(user)  # name='철수' age=25 email=None
print(user.name)  # 철수
print(user.age)  # 25
