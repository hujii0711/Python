"""예제 6: 검색 평가용 골든셋 만들기.

"검색이 잘 되나?" 를 숫자로 답하려면 질문과 정답 청크를 짝지은 데이터가 먼저 있어야 한다.
평가셋 없이 임계값이나 top_k 를 조정하는 것은 감으로 고치는 것과 같다.

여기서는 모델 없이 만들 수 있는 세 가지 방법을 쓴다.
  1) FAQ 활용    : 이미 질문과 답이 있는 자료를 그대로 쓴다. 가장 믿을 만하다.
  2) 제목 기반   : 문서 제목을 질문 형태로 바꾼다. 양은 빨리 늘지만 단조롭고 쉽다.
  3) 사람이 작성 : 실제 사용자 말투로 직접 쓴다. 문서에 없는 표현을 쓰기 때문에
                   검색이 정말 되는지 확인할 수 있는 유일한 방법이다.
                   eval/eval_questions.csv 에 있다.

정답(gold)은 청크 id 목록이다. 한 질문에 정답이 여러 개일 수 있다.
LLM 으로 질문을 생성하면 훨씬 다양해지지만 사람 검수가 필요하다 — 마지막에 설명한다.
"""

import csv
import re

from _common import (
    CHUNKS_ENRICHED,
    EVAL_DIR,
    EVAL_SET,
    RAW_DIR,
    read_jsonl,
    require,
    setup_console,
    write_jsonl,
)

# 제목을 질문으로 바꾸는 틀. 제목 형태에 따라 자연스러운 쪽을 고른다.
QUESTION_TEMPLATES = [
    "{title}에 대해 설명해주세요",
    "{title} 관련 내용을 찾아주세요",
]

SKIP_TITLES = {"", "개요", "소개"}


def from_faq(chunks: list[dict]) -> list[dict]:
    """FAQ CSV 의 질문을, 그 행에서 만들어진 청크와 연결한다.

    01 단계에서 doc_id 를 'faq#행번호' 로 고정해 두었기 때문에 행 번호만으로
    정답 청크를 찾을 수 있다. 식별자를 고정해두면 이런 연결이 쉬워진다.
    """
    rows: list[dict] = []
    path = RAW_DIR / "faq.csv"
    if not path.exists():
        return rows

    with path.open("r", encoding="utf-8-sig", newline="") as f:
        for index, row in enumerate(csv.DictReader(f)):
            doc_id = f"faq#{index}"
            gold = [c["chunk_id"] for c in chunks if c["doc_id"] == doc_id]
            if not gold:
                # 정제나 중복 제거 단계에서 빠진 행이면 평가셋에도 넣지 않는다.
                continue
            rows.append(
                {
                    "qa_id": f"faq-{index}",
                    "question": (row.get("question") or "").strip(),
                    "answer": (row.get("answer") or "").strip(),
                    "gold_chunk_ids": gold,
                    "category": row.get("category") or "faq",
                    "origin": "faq",
                }
            )
    return rows


def from_headings(chunks: list[dict]) -> list[dict]:
    """청크의 heading_path 마지막 제목을 질문으로 바꾼다."""
    rows: list[dict] = []
    seen: set[str] = set()

    for chunk in chunks:
        title = (chunk.get("section") or "").strip()
        title = re.sub(r"[.?!]+$", "", title)
        if title in SKIP_TITLES or title in seen or len(title) < 4:
            continue
        seen.add(title)

        template = QUESTION_TEMPLATES[len(rows) % len(QUESTION_TEMPLATES)]
        # 같은 제목을 가진 청크가 여러 개면 모두 정답으로 인정한다.
        gold = [c["chunk_id"] for c in chunks if (c.get("section") or "").strip() == title]
        rows.append(
            {
                "qa_id": f"head-{len(rows)}",
                "question": template.format(title=title),
                "answer": "",  # 제목 기반은 정답 문장이 없다. 검색 평가에만 쓴다.
                "gold_chunk_ids": gold,
                "category": chunk["category"],
                "origin": "heading",
            }
        )
    return rows


def resolve_gold(chunks: list[dict], gold_doc: str, gold_section: str) -> list[str]:
    """문서 이름(과 선택적으로 절 이름)으로 정답 청크 id 를 찾는다.

    doc_id 가 정확히 일치하지 않으면 접두사로도 찾는다. 중복 제거 단계에서 개정판이
    남는 경우(pandas_missing -> pandas_missing_v2)가 있어서, 질문 파일을 그때마다
    고쳐 쓰지 않아도 되게 하기 위해서다.
    """
    matched = [c for c in chunks if c["doc_id"] == gold_doc]
    if not matched:
        matched = [c for c in chunks if c["doc_id"].startswith(gold_doc)]

    if gold_section:
        narrowed = [
            c for c in matched if (c.get("section") or "").strip() == gold_section
        ]
        # 절 이름이 안 맞으면(청킹 설정이 바뀌면 생긴다) 문서 전체를 정답으로 둔다.
        if narrowed:
            return [c["chunk_id"] for c in narrowed]
    return [c["chunk_id"] for c in matched]


def from_curated(chunks: list[dict]) -> tuple[list[dict], list[str]]:
    """사람이 직접 쓴 질문. 문서 표현을 따라 쓰지 않아서 난이도가 현실적이다."""
    rows: list[dict] = []
    unresolved: list[str] = []
    path = EVAL_DIR / "eval_questions.csv"
    if not path.exists():
        return rows, unresolved

    with path.open("r", encoding="utf-8-sig", newline="") as f:
        for index, row in enumerate(csv.DictReader(f)):
            gold = resolve_gold(
                chunks,
                (row.get("gold_doc") or "").strip(),
                (row.get("gold_section") or "").strip(),
            )
            if not gold:
                unresolved.append(row.get("question") or "")
                continue
            rows.append(
                {
                    "qa_id": f"user-{index}",
                    "question": (row.get("question") or "").strip(),
                    "answer": "",
                    "gold_chunk_ids": gold,
                    "category": row.get("category") or "etc",
                    "origin": "curated",
                }
            )
    return rows, unresolved


if __name__ == "__main__":
    setup_console()

    require(CHUNKS_ENRICHED, "05_enrich_metadata.py")
    chunks = read_jsonl(CHUNKS_ENRICHED)
    print(f"입력: {len(chunks)}개 청크 ({CHUNKS_ENRICHED.name})\n")

    faq_rows = from_faq(chunks)
    heading_rows = from_headings(chunks)
    curated_rows, unresolved = from_curated(chunks)
    eval_rows = faq_rows + heading_rows + curated_rows

    written = write_jsonl(EVAL_SET, eval_rows)
    print(f"평가셋 {written}건 -> {EVAL_SET.name}")
    print(f"  FAQ 기반      : {len(faq_rows)}건 (질문과 정답이 모두 있다)")
    print(f"  제목 기반     : {len(heading_rows)}건 (검색 평가 전용, 쉬운 편)")
    print(f"  사람이 작성   : {len(curated_rows)}건 (실제 말투, 난이도가 현실적)")
    if unresolved:
        print(f"  정답 문서를 못 찾아 건너뛴 질문: {len(unresolved)}건")
        for question in unresolved:
            print(f"      {question}")

    multi = sum(1 for r in eval_rows if len(r["gold_chunk_ids"]) > 1)
    print(f"  정답이 2개 이상인 질문 : {multi}건")

    print("\n-- 카테고리 분포 --")
    by_category: dict[str, int] = {}
    for row in eval_rows:
        by_category[row["category"]] = by_category.get(row["category"], 0) + 1
    for category, count in sorted(by_category.items(), key=lambda kv: -kv[1]):
        print(f"  {category:<12} {count}건")

    print("\n-- 예시 --")
    for row in faq_rows[:1] + heading_rows[:2] + curated_rows[:3]:
        print(f"  [{row['origin']:<7}] {row['question']}")
        print(f"            정답: {row['gold_chunk_ids']}")

    print("")
    print("출처별로 난이도가 다르다는 점을 기억해야 한다")
    print("  - 제목/FAQ 기반 질문은 문서의 표현을 그대로 쓰기 때문에 거의 다 맞는다.")
    print("    이 점수만 보고 검색이 잘 된다고 판단하면 안 된다.")
    print("  - 사람이 쓴 질문은 문서에 없는 단어를 쓰므로 실제 성능에 가깝다.")
    print("    07 단계에서 출처별로 점수를 나눠 보는 이유다.")
    print("  - 양을 더 늘리려면 rag/06_rag_chain.py 의 LLM 으로 청크마다 질문을")
    print("    생성하고, 사람이 훑어보며 이상한 것을 걸러내는 방식을 쓴다.")
