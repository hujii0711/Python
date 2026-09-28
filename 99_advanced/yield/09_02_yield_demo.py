import tracemalloc


def title(text: str) -> None:
    print()
    print("=" * 60)
    print(text)
    print("=" * 60)


# ---------------------------------------------------------------------------
# 실험 2: 메모리
# ---------------------------------------------------------------------------


def squares_list(n: int) -> list[int]:
    """전부 리스트에 담아 반환한다."""
    result = []
    for i in range(n):
        result.append(i * i)
    return result


def squares_yield(n: int):
    """하나씩 흘려보낸다. 나머지 실험과 같은 def + yield 형태."""
    for i in range(n):
        yield i * i


def demo_memory(n: int = 1_000_000) -> None:
    title(f"실험 2. 메모리 사용량 ({n:,}개)")

    tracemalloc.start()
    total_list = sum(squares_list(n))  # 100만 개를 전부 메모리에 올린 뒤 더한다
    peak_list = tracemalloc.get_traced_memory()[1]
    tracemalloc.stop()

    tracemalloc.start()
    total_yield = sum(squares_yield(n))  # 하나 만들어 더하고 버리기를 반복한다
    peak_yield = tracemalloc.get_traced_memory()[1]
    tracemalloc.stop()

    # 참고: (i * i for i in range(n)) 같은 제너레이터 표현식도 위 squares_yield 와
    # 똑같은 제너레이터 객체를 만든다. 문법만 짧을 뿐 동작은 동일하다.
    tracemalloc.start()
    total_expr = sum(i * i for i in range(n))
    peak_expr = tracemalloc.get_traced_memory()[1]
    tracemalloc.stop()

    print(f"\n  리스트로 모으기      : {peak_list / 1024 / 1024:8.2f} MB")
    print(f"  yield 로 흘려보내기  : {peak_yield / 1024 / 1024:8.2f} MB")
    print(
        f"  제너레이터 표현식    : {peak_expr / 1024 / 1024:8.2f} MB  <- yield 와 같은 물건"
    )
    print(f"\n  차이 : {peak_list / max(peak_yield, 1):,.0f} 배")
    print(f"  (세 방식 모두 합계는 같다: {total_list == total_yield == total_expr})")


def main() -> None:
    demo_memory()


if __name__ == "__main__":
    main()
