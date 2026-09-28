"""
pydantic은 변환 가능한 값("25" → 25)은 자동으로 바꿔주고, 변환할 수 없으면 ValidationError를 냅니다.
중첩 구조와 list[int] 같은 요소 타입도 검사합니다. 변환 없이 엄격하게 검사하려면 Field나 ConfigDict(strict=True)를 쓰면 됩니다.

# `@dataclass`와 `BaseModel` 차이
|           | `pydantic.dataclasses.dataclass` | `BaseModel` |
|-----------|----------------------------------|-------------------------|
| 생성 방식   | 위치/키워드 인자 모두 가능              | 키워드 인자만              |
| JSON 변환  | 별도 처리 필요                       | `model_dump_json()` 내장 |
| 검증/변환   | 지원                               | 지원 (기능이 더 풍부)       |
| 용도       | 기존 dataclass 코드에 검증 추가       | API, 설정, 데이터 검증 전반   |
"""

from pydantic.dataclasses import dataclass


@dataclass
class User:
    name: str
    age: int
    tags: list[str]


u = User(name="철수", age="25", tags=["a", "b"])
print(u)  # User(name='철수', age=25, tags=['a', 'b'])  <- "25"가 int로 변환됨

User(name="철수", age="abc", tags=["a"])
# ValidationError: age - Input should be a valid integer
## 기본 모델 정의와 생성
