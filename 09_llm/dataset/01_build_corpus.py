"""예제 1: 원시 문서를 하나의 코퍼스 스키마로 모으기.

RAG 작업의 출발점은 "형식이 제각각인 파일들"을 한 가지 스키마로 통일하는 일이다.
파일마다 확장자도 인코딩도 다르므로, 읽는 방법만 분기하고 결과 레코드는 똑같이 만든다.

읽는 대상은 `raw/` 뿐이다. 평가용 질문(`eval/eval_questions.csv`)은 일부러 다른
디렉터리에 둔다. 평가 질문이 코퍼스에 섞여 색인되면 질문이 자기 자신을 검색해 맞히는
꼴이 되어 점수가 의미를 잃는다.

레코드 스키마
  doc_id     : 파일 경로 기반의 고정 식별자 (재실행해도 안 바뀐다)
  source     : 원본 파일 이름
  ext        : 확장자 (뒤 단계에서 형식별 처리를 할 때 쓴다)
  category   : 파일 이름 / CSV 열에서 뽑은 분류 (층화 분할·리포트에 쓴다)
  text       : 본문
  char_len   : 글자 수
  sha256     : 본문 해시 (정확 중복 판별용)
"""

import csv

from _common import (
    CORPUS_RAW,
    RAW_DIR,
    sha256_text,
    setup_console,
    write_jsonl,
)

# 파일 이름 앞부분으로 카테고리를 정한다. 실무에서는 디렉터리 구조나 DB 값을 쓴다.
CATEGORY_BY_PREFIX = {
    "python": "python",
    "pandas": "pandas",
    "qdrant": "qdrant",
    "embedding": "embedding",
    "chunking": "chunking",
    "search": "search",
    "eval": "evaluation",
}


def guess_category(stem: str) -> str:
    for prefix, category in CATEGORY_BY_PREFIX.items():
        if stem.startswith(prefix):
            return category
    return "etc"


def read_text_file(path) -> str:
    """텍스트 계열 파일.

    utf-8-sig 로 읽으면 BOM 이 있으면 떼고 없으면 그대로 둔다. 윈도우에서 만든
    파일에 BOM 이 붙는 일이 흔해서, 처음부터 이렇게 읽어두면 뒤에서 덜 고생한다.
    """
    return path.read_text(encoding="utf-8-sig")


def read_csv_rows(path) -> list[tuple[str, str]]:
    """CSV 는 한 행이 한 문서가 된다. (본문, 카테고리) 목록을 돌려준다."""
    rows = []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            question = (row.get("question") or "").strip()
            answer = (row.get("answer") or "").strip()
            rows.append((f"{question}\n{answer}", row.get("category") or "faq"))
    return rows


def build() -> list[dict]:
    records: list[dict] = []

    for path in sorted(RAW_DIR.iterdir()):
        if not path.is_file():
            continue
        ext = path.suffix.lower()

        # 형식별로 읽는 방법만 분기하고, 만드는 레코드 모양은 같게 맞춘다.
        if ext == ".csv":
            items = read_csv_rows(path)
        elif ext in {".md", ".txt", ".html"}:
            items = [(read_text_file(path), guess_category(path.stem))]
        else:
            print(f"  건너뜀(지원하지 않는 형식): {path.name}")
            continue

        for index, (text, category) in enumerate(items):
            # doc_id 를 파일 이름 + 행 번호로 고정하면 다시 만들어도 같은 id 가 나온다.
            doc_id = f"{path.stem}#{index}" if len(items) > 1 else path.stem
            records.append(
                {
                    "doc_id": doc_id,
                    "source": path.name,
                    "ext": ext.lstrip("."),
                    "category": category,
                    "text": text,
                    "char_len": len(text),
                    "sha256": sha256_text(text),
                }
            )

    return records


if __name__ == "__main__":
    setup_console()

    print(f"원시 디렉터리: {RAW_DIR}")
    records = build()

    written = write_jsonl(CORPUS_RAW, records)
    print(f"\n코퍼스 {written}건 -> {CORPUS_RAW.name}")

    print("\n-- 형식별 --")
    by_ext: dict[str, int] = {}
    for record in records:
        by_ext[record["ext"]] = by_ext.get(record["ext"], 0) + 1
    for ext, count in sorted(by_ext.items()):
        print(f"  {ext:>5} : {count}건")

    print("\n-- 문서 목록 --")
    for record in records:
        preview = record["text"][:40].replace("\n", " ").strip()
        print(f"  {record['char_len']:>5}자  [{record['category']:<10}] "
              f"{record['doc_id']:<20} {preview}...")
