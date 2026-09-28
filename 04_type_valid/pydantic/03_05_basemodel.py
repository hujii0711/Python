"""
딕셔너리, JSON에서 모델 만들기
"""

from pydantic import BaseModel


class User(BaseModel):
    name: str
    age: int
    email: str | None = None  # 선택 필드 (기본값 None)


data = {"name": "영희", "age": 30}
u1 = User(**data)  # 딕셔너리 언패킹
u2 = User.model_validate(data)  # 권장 방식

json_str = '{"name": "민수", "age": 28}'
u3 = User.model_validate_json(json_str)
print(u3)  # name='민수' age=28 email=None
