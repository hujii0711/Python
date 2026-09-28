from collections.abc import Iterator


def title(text: str) -> None:
    print()
    print("-" * 58)
    print(text)
    print("-" * 58)


# ===========================================================================
# 2. 호출하는 네 가지 방법
# ===========================================================================
def countdown(n: int) -> Iterator[int]:
    """인자를 받는 제너레이터. 타입 힌트는 Iterator[내보내는 타입]."""
    while n > 0:
        yield n
        n -= 1


def demo_call_styles() -> None:
    title("2. 호출하는 네 가지 방법")

    print("\n  (a) for 문 — 가장 흔하다. StopIteration 을 알아서 처리해 준다.")
    print("      ", end="")
    for i in countdown(5):
        print(i, end=" ")
    print()

    print("\n  (b) list() — 전부 꺼내 리스트로 만든다.")
    print(f"       {list(countdown(5))}")

    print("\n  (c) 다른 함수에 그대로 넘긴다 — sum, max, any, ' '.join ...")
    print(f"       sum : {sum(countdown(5))}")
    print(f"       max : {max(countdown(5))}")

    print("\n  (d) next() — 한 개씩 직접 꺼낸다. 끝나면 기본값을 받을 수도 있다.")
    gen = countdown(2)
    print(f"       {next(gen)}, {next(gen)}, {next(gen, '없음')}")

    print("\n  주의: 호출할 때마다 새 제너레이터가 생긴다. 위 (a)~(d)는 서로 별개다.")


def main() -> None:
    demo_call_styles()


if __name__ == "__main__":
    main()
