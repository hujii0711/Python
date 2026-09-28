def title(text: str) -> None:
    print()
    print("=" * 60)
    print(text)
    print("=" * 60)


# ---------------------------------------------------------------------------
# 실험 5: 리스트로는 아예 불가능한 것 — 끝이 없는 수열
# ---------------------------------------------------------------------------


def fibonacci():
    """무한 피보나치. 리스트로 만들면 영원히 끝나지 않는다."""
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b


def demo_infinite() -> None:
    title("실험 5. 끝이 없는 수열")

    picked = []
    for value in fibonacci():
        if value > 1000:
            break  # 필요한 만큼만 받고 멈춘다
        picked.append(value)

    print(f"\n  1000 이하 피보나치: {picked}")
    print("\n  리스트로 만들려면 무한 루프에 빠진다. yield 라서 가능한 일이다.")


def main() -> None:
    demo_infinite()


if __name__ == "__main__":
    main()
