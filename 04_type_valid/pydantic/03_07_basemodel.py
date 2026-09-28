"""
커스텀 검증 (field_validator)
"""

from pydantic import BaseModel, field_validator


class Signup(BaseModel):
    username: str
    password: str

    @field_validator("username")
    @classmethod
    def no_space(cls, v: str) -> str:
        if " " in v:
            raise ValueError("공백을 포함할 수 없습니다")
        return v.strip().lower()

    @field_validator("password")
    @classmethod
    def min_len(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("비밀번호는 8자 이상이어야 합니다")
        return v


Signup(username="Chulsoo", password="12345678")  # username -> 'chulsoo'
Signup(username="a b", password="123")  # ValidationError
