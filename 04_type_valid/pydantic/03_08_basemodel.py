"""
모델 설정 (ConfigDict)
"""

from pydantic import BaseModel, ConfigDict


class Item(BaseModel):
    model_config = ConfigDict(
        strict=True,  # 타입 변환 없이 엄격하게 검사
        frozen=True,  # 생성 후 수정 불가 (해시 가능)
        extra="forbid",  # 정의되지 않은 필드가 들어오면 에러
        str_strip_whitespace=True,  # 문자열 앞뒤 공백 제거
    )
    name: str
    qty: int


Item(name="펜", qty=3)  # OK
Item(name="펜", qty="3")  # strict라서 ValidationError
Item(name="펜", qty=3, x=1)  # extra="forbid"라서 ValidationError
