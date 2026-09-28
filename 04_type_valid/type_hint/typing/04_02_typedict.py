"""
일반 클래스는 "동작하는 객체" 를 만들고, TypedDict 클래스는 "딕셔너리의 생김새" 를 선언할 뿐이다.
| 항목          | 일반 클래스     | TypedDict 클래스    |
| ------------ | ------------ | ----------------- |
| 결과물         | 클래스 인스턴스  | 일반 `dict`        |
| 필드 접근      | `obj.id`      | `obj["id"]`       |
| 메서드 정의     | ✅ 가능        | ❌ 불가능           |
| 상속 확장      | ✅ 자유롭게     | ⚠️ TypedDict끼리만   |
| 런타임 타입 체크 | ✅ 동작        | ❌ 동작 안 함        |
| 목적          | 동작(로직) 정의  | 딕셔너리 구조 선언     |
"""

from typing import TypedDict


# 일반 클래스
class NormalChunk:
    def __init__(self):
        self.id = "001"


obj = NormalChunk()
type(obj)  # <class 'NormalChunk'>  ← NormalChunk 인스턴스


# TypedDict 클래스
class Chunk(TypedDict):
    id: str


obj = Chunk(id="001")
type(obj)  # <class 'dict'>  ← 그냥 딕셔너리


class Chunk(TypedDict):  # ✅ TypedDict 간 상속
    source_type: dict
    title: str
