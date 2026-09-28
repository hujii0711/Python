import time


def title(text: str) -> None:
    print()
    print("=" * 60)
    print(text)
    print("=" * 60)


# ---------------------------------------------------------------------------
# 실험 3: 첫 결과가 나오기까지 걸리는 시간
# ---------------------------------------------------------------------------
# 한 건 처리에 0.2초가 걸리는 느린 작업이라고 가정한다.


def slow_list(n: int) -> list[int]:
    result = []
    for i in range(n):
        time.sleep(0.2)
        result.append(i)
    return result


def slow_gen(n: int):
    for i in range(n):
        time.sleep(0.2)
        yield i


def demo_latency(n: int = 5) -> None:
    title("실험 3. 첫 결과가 나오기까지")

    start = time.perf_counter()
    for i, _ in enumerate(slow_list(n), start=1):
        print(f"    [리스트] {i}번째 결과 도착 ... {time.perf_counter() - start:.2f}초")

    start = time.perf_counter()
    for i, _ in enumerate(slow_gen(n), start=1):
        print(f"    [yield ] {i}번째 결과 도착 ... {time.perf_counter() - start:.2f}초")

    print("\n  차이: 리스트는 전부 끝나야 첫 결과가 나온다.")
    print("        yield 는 0.2초 만에 첫 결과가 나오고 이어서 계속 흐른다.")


def main() -> None:

    demo_latency()


if __name__ == "__main__":
    main()
