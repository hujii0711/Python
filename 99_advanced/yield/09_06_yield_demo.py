import sys


def title(text: str) -> None:
    print()
    print("=" * 60)
    print(text)
    print("=" * 60)


# ---------------------------------------------------------------------------
# 실험 6: 이 프로젝트의 실제 코드 (jsonl_to_json.iter_records)
# ---------------------------------------------------------------------------


def demo_real_module() -> None:
    title("실험 6. 실제 코드: iter_records vs load")

    sys.path.insert(
        0, str(__import__("pathlib").Path(__file__).resolve().parents[1] / "src")
    )
    try:
        from pythontest.jsonl_to_json import iter_records, load
    except ImportError as exc:  # pragma: no cover
        print(f"\n  모듈을 불러오지 못했습니다: {exc}")
        return

    import io

    jsonl = '{"id": 1}\n{"id": 2}\n{"id": 3}\n'

    records = iter_records(io.StringIO(jsonl))
    print(f"\n  iter_records(...) 호출 결과 : {records}")
    print("    -> 아직 파일을 한 줄도 안 읽었다. 꺼낼 때 비로소 읽는다.")
    print(f"    첫 줄만 꺼내 보면      : {next(records)}")
    print("    -> 나머지 두 줄은 여전히 안 읽은 상태다.")

    rows = load(io.StringIO(jsonl))
    print(f"\n  load(...) 호출 결과        : {rows}")
    print("    -> 전부 읽어서 리스트로 들고 있다. list(iter_records(...)) 와 같다.")


def main() -> None:
    demo_real_module()
    print()


if __name__ == "__main__":
    main()
