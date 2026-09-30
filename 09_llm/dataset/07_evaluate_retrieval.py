"""예제 7: 검색 품질 평가 (Recall@k, MRR, nDCG).

평가셋으로 검색 단계만 따로 채점한다. 생성 품질이 나쁠 때 검색이 문제인지 LLM 이
문제인지 구분하려면 이 단계가 먼저 있어야 한다.

지표
  Recall@k    : 정답 청크 중 몇 개가 상위 k 안에 들어왔나 (정답이 여러 개일 때 중요)
  Hit@k       : 정답이 하나라도 상위 k 안에 있었나 (0 또는 1)
  MRR         : 첫 정답의 순위 역수. 정답이 1위면 1.0, 2위면 0.5
  nDCG@k      : 순위별 가중치를 줘서 계산. 정답이 여러 개일 때 순서까지 반영한다

검색은 numpy 코사인 유사도로 직접 한다. 지표 계산이 주제라서 벡터DB 를 끼우지 않았고,
Qdrant 로 바꾸더라도 아래 retrieve() 만 갈아끼우면 나머지는 그대로다.
"""

import json

import numpy as np

from _common import (
    CHUNKS_ENRICHED,
    EVAL_SET,
    METRICS,
    encode,
    read_jsonl,
    require,
    setup_console,
)

K_VALUES = [1, 3, 5, 10]


def retrieve(query_vectors, chunk_vectors, top_k: int) -> np.ndarray:
    """질의별로 유사도 상위 top_k 청크의 인덱스를 돌려준다."""
    similarity = query_vectors @ chunk_vectors.T  # 정규화된 벡터라 내적 = 코사인
    # argsort 는 오름차순이므로 부호를 뒤집어 상위부터 나오게 한다.
    return np.argsort(-similarity, axis=1)[:, :top_k]


def recall_at_k(ranked: list[str], gold: set[str], k: int) -> float:
    return len(set(ranked[:k]) & gold) / len(gold)


def hit_at_k(ranked: list[str], gold: set[str], k: int) -> float:
    return 1.0 if set(ranked[:k]) & gold else 0.0


def reciprocal_rank(ranked: list[str], gold: set[str]) -> float:
    for rank, chunk_id in enumerate(ranked, start=1):
        if chunk_id in gold:
            return 1.0 / rank
    return 0.0


def ndcg_at_k(ranked: list[str], gold: set[str], k: int) -> float:
    """정답이면 1, 아니면 0 으로 보고 순위 할인(log2)을 적용한다.

    ideal 은 정답들이 맨 위에 몰려 있는 이상적인 경우의 점수다. 그걸로 나눠서
    0 ~ 1 로 정규화하기 때문에 질문마다 정답 개수가 달라도 비교할 수 있다.
    """
    gains = [1.0 if cid in gold else 0.0 for cid in ranked[:k]]
    dcg = sum(g / np.log2(i + 2) for i, g in enumerate(gains))
    ideal = sum(1.0 / np.log2(i + 2) for i in range(min(len(gold), k)))
    return dcg / ideal if ideal else 0.0


if __name__ == "__main__":
    setup_console()

    require(CHUNKS_ENRICHED, "05_enrich_metadata.py")
    require(EVAL_SET, "06_make_eval_set.py")
    chunks = read_jsonl(CHUNKS_ENRICHED)
    eval_rows = read_jsonl(EVAL_SET)
    print(f"청크 {len(chunks)}개 / 평가 질문 {len(eval_rows)}건\n")

    print("임베딩 중...")
    chunk_ids = [c["chunk_id"] for c in chunks]
    chunk_vectors = encode([c["text"] for c in chunks])
    query_vectors = encode([r["question"] for r in eval_rows])

    max_k = min(max(K_VALUES), len(chunks))
    top_indices = retrieve(query_vectors, chunk_vectors, max_k)

    per_query = []
    for row, indices in zip(eval_rows, top_indices):
        ranked = [chunk_ids[i] for i in indices]
        gold = set(row["gold_chunk_ids"])
        per_query.append(
            {
                "qa_id": row["qa_id"],
                "origin": row["origin"],
                "question": row["question"],
                "rr": reciprocal_rank(ranked, gold),
                "top1": ranked[0],
                "gold": sorted(gold),
                **{f"recall@{k}": recall_at_k(ranked, gold, k) for k in K_VALUES},
                **{f"hit@{k}": hit_at_k(ranked, gold, k) for k in K_VALUES},
                **{f"ndcg@{k}": ndcg_at_k(ranked, gold, k) for k in K_VALUES},
            }
        )

    def mean(field: str, rows=None) -> float:
        rows = per_query if rows is None else rows
        return sum(r[field] for r in rows) / len(rows) if rows else 0.0

    print("\n-- 전체 지표 --")
    print(f"  {'k':>3}  {'Recall@k':>9}{'Hit@k':>9}{'nDCG@k':>9}")
    for k in K_VALUES:
        print(f"  {k:>3}  {mean(f'recall@{k}'):>9.3f}{mean(f'hit@{k}'):>9.3f}"
              f"{mean(f'ndcg@{k}'):>9.3f}")
    print(f"\n  MRR = {mean('rr'):.3f}")

    print("\n-- 질문 출처별 (제목 기반이 쉬운지 확인) --")
    for origin in sorted({r["origin"] for r in per_query}):
        rows = [r for r in per_query if r["origin"] == origin]
        print(f"  {origin:<8} {len(rows):>2}건  "
              f"Recall@3={mean('recall@3', rows):.3f}  MRR={mean('rr', rows):.3f}")

    print("\n-- 못 맞힌 질문 (Recall@3 = 0) --")
    misses = [r for r in per_query if r["recall@3"] == 0.0]
    for row in misses:
        print(f"  {row['qa_id']:<8} {row['question']}")
        print(f"           정답 {row['gold']} / 1위로 뽑힌 것 {row['top1']}")
    if not misses:
        print("  없음")

    summary = {
        "chunks": len(chunks),
        "queries": len(eval_rows),
        "mrr": round(mean("rr"), 4),
        **{f"recall@{k}": round(mean(f"recall@{k}"), 4) for k in K_VALUES},
        **{f"hit@{k}": round(mean(f"hit@{k}"), 4) for k in K_VALUES},
        **{f"ndcg@{k}": round(mean(f"ndcg@{k}"), 4) for k in K_VALUES},
    }
    METRICS.parent.mkdir(parents=True, exist_ok=True)
    METRICS.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n요약 지표 -> {METRICS.name}")
    print("설정을 바꿀 때마다 이 파일을 남겨두면 어떤 변경이 도움이 됐는지 비교할 수 있다.")
