from collections.abc import Iterator


def title(text: str) -> None:
    print()
    print("-" * 58)
    print(text)
    print("-" * 58)


# ===========================================================================
# 6. 실전 형태 — 파일을 한 줄씩 (이 프로젝트 iter_records 와 같은 구조)
# ===========================================================================


def read_lines(text: str) -> Iterator[tuple[int, str]]:
    """줄 번호와 내용을 함께 내보낸다. 빈 줄은 건너뛴다."""
    for lineno, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line:
            continue  # 아무것도 yield 하지 않으면 그 줄은 그냥 건너뛴 것이 된다
        yield lineno, line


def demo_real_shape() -> None:
    title("6. 실전 형태 — 줄 단위로 흘려보내기")

    sample = "첫 줄\n\n  셋째 줄  \n\n다섯째 줄\n"
    print("\n  입력 (빈 줄 포함):")
    for lineno, line in read_lines(sample):
        print(f"    {lineno}번째: {line!r}")

    print("\n  튜플을 yield 하면 for 문에서 바로 풀어 받을 수 있다.")
    print("  jsonl_to_json.iter_records 도 이 구조다 — 읽는 즉시 하나씩 내보낸다.")


def main() -> None:
    demo_real_shape()


if __name__ == "__main__":
    main()
