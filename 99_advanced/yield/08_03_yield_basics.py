from collections.abc import Iterator


def title(text: str) -> None:
    print()
    print("-" * 58)
    print(text)
    print("-" * 58)


# ===========================================================================
# 3. 조건에 따라 걸러 내보내기 (필터 형태)
# ===========================================================================
# yield 는 루프 안, if 안, 어디에 놔도 된다. 실행이 그 줄에 닿을 때 하나 나간다.


def evens_only(numbers) -> Iterator[int]:
    for n in numbers:
        if n % 2 == 0:
            yield n  # 짝수일 때만 내보낸다. 홀수면 그냥 다음 반복으로.


def demo_filter() -> None:
    title("3. 조건부 yield")

    data = [1, 2, 3, 4, 5, 6, 7, 8]
    print(f"\n  입력   : {data}")
    print(f"  짝수만 : {list(evens_only(data))}")


def main() -> None:
    demo_filter()


if __name__ == "__main__":
    main()
