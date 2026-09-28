"""
한 줄 요약: `field()`는 기본값 설정을 넘어 초기화·출력·비교 동작까지 세밀하게 제어하는 도구입니다.
"""

from dataclasses import dataclass, field


# field() 없이 — 기본값만 지정 가능
@dataclass
class Simple:
    name: str = "홍길동"
    tags: list = []  # ❌ 오류! 가변 객체는 직접 기본값 불가


# field() 사용 — 세부 동작 제어 가능
@dataclass
class Advanced:
    name: str = field(default="홍길동", repr=True)
    tags: list = field(default_factory=list)  # ✅ 인스턴스마다 새 리스트
    password: str = field(default="1234", repr=False)  # print시 숨김


a = Advanced()
b = Advanced()

a.tags.append("python")

print(a.tags)  # ['python']
print(b.tags)  # []  ← 독립적인 리스트 (default_factory 덕분)

print(a)  # Advanced(name='홍길동', tags=['python'])
# password는 repr=False 라 출력 안 됨
