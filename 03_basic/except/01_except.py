"""
# 자주 만나는 예외
| 예외 | 발생 상황 |
|---------------------|---------------------------|
| `ValueError`        | `int("abc")` 처럼 값이 부적절 |
| `TypeError`         | `"a" + 1` 처럼 타입이 맞지 않음 |
| `KeyError`          | 딕셔너리에 없는 키 접근 |
| `IndexError`        | 리스트 범위를 벗어난 인덱스 |
| `FileNotFoundError` | 없는 파일 열기 |
| `ZeroDivisionError` | 0으로 나누기 |
| `AttributeError`    | 없는 속성/메서드 접근 |
| `ImportError`       | 모듈 import 실패 |

# 팁
- 예외는 가능한 한 구체적인 타입으로 잡으세요. except Exception은 최후의 보루로만 쓰는 게 좋습니다.
- except: pass처럼 예외를 조용히 삼키면 나중에 원인을 찾기 매우 어려워집니다.
- 예외가 자주 발생하는 흐름은 if로 미리 검사하는 편이 낫고, 드물게 발생하는 실패 상황에 예외 처리를 쓰는 게 파이썬다운 방식입니다.
"""

try:
    result = 10 / 0
except ZeroDivisionError:
    print("0으로 나눌 수 없습니다")
