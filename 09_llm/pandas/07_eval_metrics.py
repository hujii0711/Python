"""07. 검색 품질 평가 — recall@k / MRR / nDCG

RAG 를 개선하려면 측정해야 한다. 평가 데이터는 (쿼리, 정답문서) 쌍이고,
검색 결과는 (쿼리, 문서, 순위) 표다. 둘을 merge 하고 groupby 로 집계한다.
"""

import numpy as np
import pandas as pd

# --- 정답 세트 (쿼리별로 정답 문서가 여러 개일 수 있다) ---
truth = pd.DataFrame(
    {
        "query_id": ["Q1", "Q1", "Q2", "Q3", "Q3", "Q3", "Q4"],
        "doc_id": ["D1", "D5", "D2", "D3", "D7", "D9", "D4"],
        "relevance": [3, 1, 3, 3, 2, 1, 3],  # nDCG 용 등급 (0=무관)
    }
)

# --- 검색 결과 (순위 포함) ---
results = pd.DataFrame(
    {
        "query_id": ["Q1"] * 5 + ["Q2"] * 5 + ["Q3"] * 5 + ["Q4"] * 5,
        "doc_id": [
            "D1", "D8", "D5", "D6", "D7",  # Q1: 1위 정답, 3위 정답
            "D9", "D2", "D4", "D1", "D3",  # Q2: 2위 정답
            "D7", "D6", "D9", "D8", "D3",  # Q3: 1,3,5위 정답
            "D1", "D2", "D3", "D5", "D6",  # Q4: 정답 없음
        ],
        "rank": list(range(1, 6)) * 4,
        "score": np.tile([0.91, 0.85, 0.80, 0.72, 0.65], 4),
    }
)

print("-- 검색 결과에 정답 표시 --")
# how='left' 로 검색 결과 기준 조인. 정답이 아니면 relevance 가 NaN.
ev = results.merge(truth, on=["query_id", "doc_id"], how="left")
ev["relevance"] = ev["relevance"].fillna(0).astype(int)
ev["is_hit"] = ev["relevance"] > 0
print(ev.to_string(index=False))

K = 5

# --- 1) recall@k: 정답 중 몇 개를 찾았나 ---
n_truth = truth.groupby("query_id").size().rename("n_truth")
n_found = ev[ev["is_hit"]].groupby("query_id").size().rename("n_found")
recall = pd.concat([n_truth, n_found], axis=1).fillna(0)
recall["recall@5"] = recall["n_found"] / recall["n_truth"]

print(f"\n-- recall@{K} --")
print(recall.to_string())
print(f"평균: {recall['recall@5'].mean():.4f}")

# --- 2) precision@k: 검색 결과 중 몇 개가 정답인가 ---
prec = ev.groupby("query_id")["is_hit"].sum() / K
print(f"\n-- precision@{K} --")
print(prec.round(4).to_string())
print(f"평균: {prec.mean():.4f}")

# --- 3) MRR: 첫 정답의 순위 역수 ---
# 정답이 하나도 없으면 0. idxmin/first 로 첫 히트를 찾는다.
hits = ev[ev["is_hit"]]
first_hit = hits.groupby("query_id")["rank"].min().rename("first_hit_rank")
mrr = pd.DataFrame(index=recall.index).join(first_hit)
mrr["rr"] = (1 / mrr["first_hit_rank"]).fillna(0)

print("\n-- MRR --")
print(mrr.to_string())
print(f"MRR: {mrr['rr'].mean():.4f}")
print("  Q4 는 정답을 못 찾아 0. reciprocal rank 는 1위를 특히 크게 보상한다.")


# --- 4) nDCG@k: 등급을 반영한 순위 품질 ---
def dcg(relevances):
    """DCG = sum( rel_i / log2(i+1) ), i 는 1부터."""
    rel = np.asarray(relevances, dtype=float)
    positions = np.arange(1, len(rel) + 1)
    return float((rel / np.log2(positions + 1)).sum())


ndcg_rows = []
for qid, group in ev.sort_values("rank").groupby("query_id"):
    actual = dcg(group["relevance"].to_numpy())
    # IDCG: 가능한 최선의 순서 (정답을 등급 내림차순으로 배치)
    ideal_rels = truth.loc[truth["query_id"] == qid, "relevance"].sort_values(ascending=False)
    ideal = dcg(ideal_rels.head(K).to_numpy())
    ndcg_rows.append(
        {"query_id": qid, "DCG": actual, "IDCG": ideal, "nDCG@5": actual / ideal if ideal else 0.0}
    )

ndcg = pd.DataFrame(ndcg_rows).set_index("query_id")
print(f"\n-- nDCG@{K} --")
print(ndcg.round(4).to_string())
print(f"평균: {ndcg['nDCG@5'].mean():.4f}")

# --- 5) 전체 요약 ---
summary = pd.concat(
    [recall["recall@5"], prec.rename("precision@5"), mrr["rr"].rename("RR"), ndcg["nDCG@5"]],
    axis=1,
).fillna(0)
print("\n-- 쿼리별 종합 --")
print(summary.round(4).to_string())
print("\n-- 전체 평균 --")
print(summary.mean().round(4).to_string())

# --- 6) 두 설정(A/B) 비교 ---
# 실무에서 가장 많이 하는 일. 청킹 크기나 임베딩 모델을 바꿔보고 비교한다.
print("\n-- A/B 비교 --")
rng = np.random.default_rng(0)
comparison = pd.DataFrame(
    {
        "query_id": recall.index,
        "A_chunk256": summary["nDCG@5"].to_numpy(),
        "B_chunk512": np.clip(summary["nDCG@5"].to_numpy() + rng.normal(0, 0.15, len(summary)), 0, 1),
    }
).set_index("query_id")
comparison["차이"] = comparison["B_chunk512"] - comparison["A_chunk256"]
print(comparison.round(4).to_string())
print("\n평균 nDCG: A={:.4f}  B={:.4f}  차이={:+.4f}".format(
    comparison["A_chunk256"].mean(), comparison["B_chunk512"].mean(), comparison["차이"].mean()
))
print(f"B 가 더 나은 쿼리: {(comparison['차이'] > 0).sum()}/{len(comparison)}건")
print("  쿼리 수가 적으면 평균 차이는 우연일 수 있다. 쿼리별 승패도 함께 봐야 한다.")
