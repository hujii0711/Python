"""
`field()`는 dataclass의 각 필드에 상세 옵션을 부여하는 함수입니다.
단순 타입 힌트만으로는 설정할 수 없는 동작을 지정할 때 사용합니다.

- 옵션별 설명
| 옵션                | 타입   | 설명                                  |
| ----------------- | ---- | -------------------------------------- |
| `default`         | 값    | 기본값 직접 지정                           |
| `default_factory` | 함수  | 인스턴스 생성마다 호출해서 기본값 생성           |
| `repr`            | bool | `print(obj)` 출력에 포함 여부 (기본 `True`) |
| `init`            | bool | `__init__` 파라미터 포함 여부 (기본 `True`)  |
| `compare`         | bool | ==, <  비교 시 포함 여부 (기본 `True`)      |
| `hash`            | bool | `__hash__` 계산에 포함 여부                |
| `metadata`        | dict | 필드에 임의 메타데이터 부착                   |

- `Literal`: "이 값들 중 하나여야 한다"는 표시
- `TypedDict`: dict의 구조를 문서화하는 표시 (여전히 진짜 dict)
- `dataclass`: 클래스 작성을 편하게 해주는 문법 설탕, 검증은 없음
- `pydantic.BaseModel`: 위 모든 타입 힌트를 읽어서 실제로 검증하고 변환까지 해주는 런타임 엔진

"""

from dataclasses import dataclass, field


@dataclass
class Example:
    # 1. default — 단순 기본값
    name: str = field(default="홍길동")

    # 2. default_factory — 호출 가능한 객체로 기본값 생성
    # `field(default_factory=list)`는 "기본값 자체를 저장하는 게 아니라, 인스턴스가 생성될 때마다 `list()`라는 함수를 새로 호출해서 그 결과를 기본값으로 써라"라는 뜻입니다.
    # 인스턴스마다 독립된 새 리스트가 생성됨
    # 왜 필요한가: 리스트, 딕셔너리, 세트 같은 가변(mutable) 객체를 기본값으로 쓰면, 모든 인스턴스가 그 객체 하나를 공유해버리는 파이썬의 근본적인 함정이 있어요.
    # `default_factory`는 "매번 새로 만들어라"는 지시를 통해 이 함정을 피하게 해주는 dataclass의 안전장치입니다.
    tags: list = field(default_factory=list)

    # 3. repr — __repr__ 출력에서 제외
    password: str = field(default="secret", repr=False)

    # 4. init — 생성자(__init__) 파라미터에서 제외
    created_at: str = field(default="2024", init=False)

    # 5. compare — 동등 비교(__eq__)에서 제외
    score: int = field(default=0, compare=False)
