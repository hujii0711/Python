from collections.abc import Callable

# from typing import Callable
# 파이썬 3.9 버전(PEP 585)부터 기존 typing.Callable 대신 collections.abc.Callable을 사용하는 것이 공식적으로 권장(Standard)되고 있습니다.


# 인자 없고 int 반환
def run(func: Callable[[], int]) -> int:
    return func()


# int 두 개 받고 bool 반환
def filter_data(data: list[int], predicate: Callable[[int], bool]) -> list[int]:
    return [x for x in data if predicate(x)]


# 사용 예
result = filter_data([1, 2, 3, 4], lambda x: x > 2)
