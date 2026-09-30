"""08. groupby 로 청크 점수를 문서 점수로 — 재순위화

벡터DB 는 청크를 돌려주는데, 사용자에게 보여줄 단위는 문서다.
청크 여러 개가 같은 문서에서 나오면 합쳐야 하고, 문서별 다양성도 챙겨야 한다.
"""

import pandas as pd

hits = pd.DataFrame(
    {
        "chunk_id": ["C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "C9", "C10"],
        "doc_id": ["D1", "D1", "D1", "D2", "D2", "D3", "D3", "D3", "D3", "D4"],
        "title": ["파이썬 기초"] * 3 + ["판다스 입문"] * 2 + ["넘파이 가이드"] * 4 + ["기타"],
        "score": [0.91, 0.72, 0.55, 0.88, 0.85, 0.61, 0.60, 0.59, 0.58, 0.40],
        "category": ["python"] * 3 + ["pandas"] * 2 + ["numpy"] * 4 + ["etc"],
    }
)

print("-- 벡터DB 가 돌려준 청크 top-10 --")
print(hits.to_string(index=False))

# --- 1) 문서별 집계: 여러 방식을 한 번에 ---
doc_scores = hits.groupby(["doc_id", "title"], as_index=False).agg(
    max_score=("score", "max"),
    mean_score=("score", "mean"),
    sum_score=("score", "sum"),
    n_chunks=("chunk_id", "count"),
    best_chunk=("score", "idxmax"),  # 최고 점수 청크의 인덱스
)
doc_scores["best_chunk"] = hits.loc[doc_scores["best_chunk"], "chunk_id"].to_numpy()

print("\n-- 문서별 집계 --")
print(doc_scores.to_string(index=False))

# --- 2) 집계 방식에 따라 순위가 달라진다 ---
print("\n-- 집계 방식별 문서 순위 --")
for col in ("max_score", "mean_score", "sum_score", "n_chunks"):
    order = doc_scores.sort_values(col, ascending=False)["doc_id"].tolist()
    print(f"  {col:11s}: {order}")
print("\n  max  : 한 군데라도 정답이 있으면 상위. QA 형 RAG 의 기본값.")
print("  mean : 문서 전체가 고르게 관련된 경우 유리. 긴 문서에 불리.")
print("  sum  : 청크가 많은 문서가 무조건 유리해진다. 보통 쓰면 안 된다.")
print("         D3 는 점수가 다 낮은데 청크 4개라 sum 에서 1등이 된다.")

# --- 3) transform: 집계값을 원래 행에 붙이기 ---
# groupby.agg 는 행이 줄지만, transform 은 원래 행 수를 유지한다.
hits["doc_max"] = hits.groupby("doc_id")["score"].transform("max")
hits["doc_rank_in"] = hits.groupby("doc_id")["score"].rank(ascending=False, method="first").astype(int)
hits["score_ratio"] = (hits["score"] / hits["doc_max"]).round(3)

print("\n-- transform 으로 문서 내 순위/비율 --")
print(hits[["chunk_id", "doc_id", "score", "doc_max", "doc_rank_in", "score_ratio"]].to_string(index=False))

# --- 4) 문서당 최고 청크만 남기기 (중복 제거) ---
# LLM 컨텍스트를 아끼려면 문서별 대표 청크 1개씩만 넘긴다.
best_per_doc = hits[hits["doc_rank_in"] == 1].sort_values("score", ascending=False)
print("\n-- 문서별 대표 청크 1개씩 --")
print(best_per_doc[["chunk_id", "doc_id", "title", "score"]].to_string(index=False))
print(f"청크 {len(hits)}개 -> {len(best_per_doc)}개 (컨텍스트 {1 - len(best_per_doc) / len(hits):.0%} 절약)")

# --- 5) 문서당 최대 N개 (head) ---
TOP_PER_DOC = 2
limited = (
    hits.sort_values("score", ascending=False)
    .groupby("doc_id", sort=False)
    .head(TOP_PER_DOC)
    .sort_values("score", ascending=False)
)
print(f"\n-- 문서당 최대 {TOP_PER_DOC}개 --")
print(limited[["chunk_id", "doc_id", "score"]].to_string(index=False))
print("  groupby.head() 는 그룹별 상위 N개를 남긴다. 정렬을 먼저 해야 의미가 있다.")

# --- 6) 카테고리 다양성 확보 ---
# 한 카테고리가 결과를 독점하지 않게 라운드로빈으로 섞는다.
print("\n-- 카테고리 라운드로빈 --")
ranked = hits.sort_values("score", ascending=False).copy()
ranked["cat_rank"] = ranked.groupby("category").cumcount()  # 카테고리 내 순번
# 카테고리 내 순번을 1차 키, 점수를 2차 키로 정렬하면 카테고리가 번갈아 나온다
diverse = ranked.sort_values(["cat_rank", "score"], ascending=[True, False])
print(diverse[["chunk_id", "category", "score", "cat_rank"]].head(8).to_string(index=False))
print("\n  단순 점수순  :", ranked.head(5)["category"].tolist())
print("  라운드로빈   :", diverse.head(5)["category"].tolist())

# --- 7) 최종 컨텍스트 조립 ---
print("\n-- LLM 에 넘길 컨텍스트 --")
context = (
    best_per_doc.head(3)
    .assign(block=lambda d: "[" + d["title"] + " / " + d["chunk_id"] + "] score=" + d["score"].round(3).astype(str))
)
print("\n".join(context["block"]))
print(f"\n최종 {len(context)}개 문서 블록")
