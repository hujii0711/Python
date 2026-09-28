from collections.abc import Iterator


def title(text: str) -> None:
    print()
    print("-" * 58)
    print(text)
    print("-" * 58)


# ===========================================================================
# 5. yield from — 다른 제너레이터에게 넘기기
# ===========================================================================


def inner() -> Iterator[str]:
    yield "안"
    yield "쪽"


def outer() -> Iterator[str]:
    yield "["
    yield from inner()  # inner 가 내보내는 걸 그대로 흘려보낸다
    yield "]"


def demo_yield_from() -> None:
    title("5. yield from — 위임")

    print(f"\n  {''.join(outer())}")
    print("\n  yield from inner() 는 아래와 같은 뜻이다:")
    print("      for value in inner():")
    print("          yield value")


def main() -> None:
    demo_yield_from()


if __name__ == "__main__":
    main()
