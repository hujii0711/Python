from collections.abc import Iterator


def title(text: str) -> None:
    print()
    print("-" * 58)
    print(text)
    print("-" * 58)


# ===========================================================================
# 4. return 으로 끝내기 / 반환값 받기
# ===========================================================================
# 제너레이터 안의 return 은 '값을 돌려주는' 게 아니라 '거기서 끝'이라는 뜻이다.
# 굳이 값을 붙이면 StopIteration.value 에 실려 온다.


def take_until_zero(numbers) -> Iterator[int]:
    count = 0
    for n in numbers:
        if n == 0:
            return f"0을 만나 {count}개에서 멈췄습니다"  # 여기서 종료
        count += 1
        yield n


def demo_return() -> None:
    title("4. return — 도중에 끝내기")

    print(f"\n  [1, 2, 0, 3, 4] -> {list(take_until_zero([1, 2, 0, 3, 4]))}")
    print("    0 뒤의 3, 4 는 나오지 않는다.")

    print("\n  return 에 붙인 값을 받고 싶다면:")
    gen = take_until_zero([1, 2, 0, 3, 4])
    try:
        while True:
            next(gen)
    except StopIteration as stop:
        print(f"    StopIteration.value = {stop.value!r}")


def main() -> None:
    demo_return()


if __name__ == "__main__":
    main()
