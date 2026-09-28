"""
에러를 잡아서 처리할 수도 있습니다.
"""

from pydantic import BaseModel, ValidationError


class User(BaseModel):
    name: str
    age: int
    email: str | None = None  # 선택 필드 (기본값 None)


try:
    User(name="민수", age="abc")
except ValidationError as e:
    print(e.errors())  # 에러 목록 (딕셔너리 리스트)
