from typing import TypeVar

T = TypeVar("T")


def first(items: list[T]) -> T:
    return items[0]


first([1, 2, 3])  # int 반환
first(["a", "b", "c"])  # str 반환
