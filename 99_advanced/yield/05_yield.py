"""
yield from (중첩 제너레이터)
`yield from inner()` 는 `for value in inner(): yield value` 와 같은 뜻입니다.
"""


def inner():
    yield 1
    yield 2


def outer():
    yield from inner()  # inner의 yield를 그대로 위임
    yield from [3, 4, 5]  # 이터러블도 가능
    yield 6


print(list(outer()))  # [1, 2, 3, 4, 5, 6]
