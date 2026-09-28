def title(text: str) -> None:
    print()
    print("=" * 60)
    print(text)
    print("=" * 60)


# ---------------------------------------------------------------------------
# 실험 1: 함수 몸통이 "언제" 실행되는가
# ---------------------------------------------------------------------------
# 두 함수는 하는 일이 똑같다. 리스트로 모으느냐, yield 로 흘려보내느냐만 다르다.


def make_list(n: int) -> list[int]:
    result = []
    for i in range(1, n + 1):
        print(f"    [만드는 중] {i}")
        result.append(i * i)
    return result


def make_gen(n: int):
    for i in range(1, n + 1):
        print(f"    [만드는 중] {i}")
        yield i * i


def demo_when_it_runs() -> None:
    title("실험 1. 함수 몸통이 언제 실행되나")

    print("\n[리스트] 호출하는 순간 ...")
    values = make_list(3)
    print(f"  -> 호출이 끝났다. 결과: {values}")
    print("  이제 하나씩 꺼내 본다:")
    for v in values:
        print(f"    [받음] {v}")

    print("\n[yield] 호출하는 순간 ...")
    gen = make_gen(3)
    print(f"  -> 아무것도 출력되지 않았다. 결과: {gen}")
    print("  이제 하나씩 꺼내 본다:")
    for v in gen:
        print(f"    [받음] {v}")

    print("\n  차이: 리스트는 '만들기'가 다 끝난 뒤 '받기'가 시작된다.")
    print("        yield 는 만들기와 받기가 한 개씩 번갈아 일어난다.")


def main() -> None:
    demo_when_it_runs()


if __name__ == "__main__":
    main()
