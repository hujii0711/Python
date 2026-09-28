from dataclasses import dataclass, field


@dataclass(frozen=True)  # 불변 객체 (immutable)
class Point:
    x: float
    y: float


@dataclass(order=True)  # 비교 연산자 자동 생성 (<, >, <=, >=)
class Score:
    value: int
    name: str


# 기본값 설정
@dataclass
class Config:
    host: str = "localhost"
    port: int = 8080
    tags: list = field(default_factory=list)  # 가변 기본값은 field() 사용!
