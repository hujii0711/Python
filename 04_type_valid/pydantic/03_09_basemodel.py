"""
모델 복사와 수정
"""

from pydantic import BaseModel


class User(BaseModel):
    name: str
    age: int
    email: str | None = None  # 선택 필드 (기본값 None)


u = User(name="철수", age=25)
u2 = u.model_copy(update={"age": 26})
print(u2.age)  # 26 (원본 u는 그대로)
