"""
반드시 try / finally로 감싸기
with 블록 안에서 예외가 나면 그 예외가 yield 지점에서 다시 발생합니다. try/finally가 없으면 teardown 코드가 실행되지 않습니다.
"""

from contextlib import contextmanager


# 나쁜 예: 예외가 나면 "정리"가 출력되지 않음
@contextmanager
def bad():
    print("준비")
    yield
    print("정리")


# 좋은 예
@contextmanager
def good():
    print("준비")
    try:
        yield
    finally:
        print("정리")  # 예외가 나도 실행됨


with good():
    raise ValueError("오류 발생")
# 준비
# 정리
# ValueError: 오류 발생
