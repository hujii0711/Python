"""예제 10: 데이터셋 카드(리포트) 만들기.

데이터셋은 계속 바뀐다. 문서가 추가되고 청킹 설정이 바뀌고 정제 규칙이 늘어난다.
어느 시점 데이터로 그 점수가 나왔는지 남겨두지 않으면 나중에 비교가 불가능하다.

카드에 남기는 것
  - 단계별 건수 변화 (원시 -> 정제 -> 중복 제거 -> 청킹)
  - 길이 / 카테고리 / 언어 분포
  - split 크기와 누수 여부
  - 검색 평가 지표
  - 산출물 체크섬 (같은 데이터인지 확인하는 용도)

Markdown 으로 저장해서 git 에 함께 커밋하면 변경 이력이 그대로 남는다.
"""

import hashlib
import json
from datetime import date

import pandas as pd

from _common import (
    BUILD_DIR,
    CHUNKS_ENRICHED,
    CORPUS_CLEAN,
    CORPUS_DEDUP,
    CORPUS_RAW,
    DATASET_CARD,
    EVAL_SET,
    METRICS,
    SPLITS,
    TRIPLETS,
    read_jsonl,
    require,
    setup_console,
)

STAGES = [
    ("01 원시 수집", CORPUS_RAW, "문서"),
    ("02 정제", CORPUS_CLEAN, "문서"),
    ("03 중복 제거", CORPUS_DEDUP, "문서"),
    ("04 청킹", CHUNKS_ENRICHED, "청크"),
    ("06 평가셋", EVAL_SET, "질문"),
    ("08 트리플렛", TRIPLETS, "묶음"),
    ("09 분할", SPLITS, "청크"),
]


def file_digest(path) -> str:
    """파일 내용 해시. 같은 데이터로 낸 결과인지 확인할 때 쓴다."""
    if not path.exists():
        return "-"
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def count_lines(path) -> int:
    if not path.exists():
        return 0
    with path.open("r", encoding="utf-8") as f:
        return sum(1 for line in f if line.strip())


def table(frame: pd.DataFrame) -> str:
    """DataFrame 을 마크다운 표로. 열 이름과 값만 쓰는 단순한 형태."""
    header = "| " + " | ".join(str(c) for c in frame.columns) + " |"
    divider = "| " + " | ".join("---" for _ in frame.columns) + " |"
    rows = [
        "| " + " | ".join(str(v) for v in row) + " |"
        for row in frame.itertuples(index=False)
    ]
    return "\n".join([header, divider, *rows])


if __name__ == "__main__":
    setup_console()

    require(SPLITS, "09_split_dataset.py")
    chunks = read_jsonl(SPLITS)
    frame = pd.DataFrame(chunks)

    lines: list[str] = []
    add = lines.append

    add("# RAG 데이터셋 카드")
    add("")
    add(f"생성일: {date.today().isoformat()}")
    add("")

    add("## 단계별 건수")
    add("")
    stage_rows = [
        {"단계": name, "단위": unit, "건수": count_lines(path),
         "체크섬": file_digest(path)}
        for name, path, unit in STAGES
    ]
    add(table(pd.DataFrame(stage_rows)))
    add("")

    add("## 길이 분포 (청크)")
    add("")
    stats = frame[["char_len", "token_len"]].describe(
        percentiles=[0.5, 0.95]
    ).round(1)
    stats_frame = stats.reset_index().rename(columns={"index": "통계"})
    add(table(stats_frame))
    add("")

    add("## 카테고리 분포")
    add("")
    category = (
        frame.groupby("category")
        .agg(청크수=("chunk_id", "count"), 문서수=("doc_id", "nunique"))
        .reset_index()
        .sort_values("청크수", ascending=False)
    )
    add(table(category))
    add("")

    add("## 언어 분포")
    add("")
    lang = frame["lang"].value_counts().reset_index()
    lang.columns = ["언어", "청크수"]
    add(table(lang))
    add("")

    add("## split")
    add("")
    split_rows = (
        frame.groupby("split")
        .agg(청크수=("chunk_id", "count"), 문서수=("doc_id", "nunique"))
        .reset_index()
    )
    add(table(split_rows))
    add("")
    leaked = frame.groupby("doc_id")["split"].nunique()
    leaked_count = int((leaked > 1).sum())
    add(f"여러 split 에 걸친 문서: **{leaked_count}개** (0 이어야 정상)")
    add("")

    add("## 검색 평가")
    add("")
    if METRICS.exists():
        metrics = json.loads(METRICS.read_text(encoding="utf-8"))
        metric_rows = [{"지표": k, "값": v} for k, v in metrics.items()]
        add(table(pd.DataFrame(metric_rows)))
    else:
        add("아직 없음. 07_evaluate_retrieval.py 를 실행하세요.")
    add("")

    add("## 재현 방법")
    add("")
    add("```")
    add("uv run dataset/01_build_corpus.py")
    add("uv run dataset/02_clean_text.py")
    add("uv run dataset/03_dedup.py")
    add("uv run dataset/04_chunk_and_stats.py")
    add("uv run dataset/05_enrich_metadata.py")
    add("uv run dataset/06_make_eval_set.py")
    add("uv run dataset/07_evaluate_retrieval.py")
    add("uv run dataset/08_hard_negatives.py")
    add("uv run dataset/09_split_dataset.py")
    add("uv run dataset/10_dataset_report.py")
    add("```")
    add("")

    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    DATASET_CARD.write_text("\n".join(lines), encoding="utf-8")

    print(f"데이터셋 카드 -> {DATASET_CARD}")
    print()
    print("\n".join(lines[:40]))
    print("...")
