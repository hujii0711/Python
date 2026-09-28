def title(text: str) -> None:
    print()
    print("=" * 60)
    print(text)
    print("=" * 60)


# ---------------------------------------------------------------------------
# 실험 4: 제너레이터는 한 번 쓰면 끝 (yield 를 쓸 때 치르는 대가)
# ---------------------------------------------------------------------------


def demo_one_shot() -> None:
    title("실험 4. 두 번 순회하면?")

    values = [1, 2, 3]
    print(f"\n  [리스트] 1차: {list(values)}")
    print(f"  [리스트] 2차: {list(values)}   <- 몇 번이든 다시 볼 수 있다")

    gen = (v for v in [1, 2, 3])
    print(f"\n  [yield ] 1차: {list(gen)}")
    print(f"  [yield ] 2차: {list(gen)}          <- 비어 있다! 이미 다 써 버렸다")

    print("\n  len() 도 안 된다:")
    try:
        len(v for v in [1, 2, 3])
    except TypeError as exc:
        print(f"    TypeError: {exc}")

    print("\n  그래서 다시 봐야 하면 list() 로 한 번 붙잡아 둬야 한다.")


def main() -> None:
    demo_one_shot()


if __name__ == "__main__":
    main()
