"""07. 하이브리드 검색 점수 결합 — RRF / min-max / z-score

벡터 검색(의미)과 키워드 검색(BM25)은 점수 범위가 완전히 다르다.
그냥 더하면 큰 쪽이 결과를 지배한다. 스케일을 맞추거나 순위만 쓴다.
"""

import numpy as np

# 문서 8개에 대한 두 검색기의 점수 (같은 문서 집합, 스케일이 다름)
doc_ids = np.arange(8)
vector_scores = np.array([0.91, 0.88, 0.85, 0.71, 0.66, 0.52, 0.40, 0.31], dtype=np.float32)
bm25_scores = np.array([2.1, 18.4, 0.0, 11.2, 0.0, 25.7, 7.3, 0.0], dtype=np.float32)

print("-- 입력 --")
print("벡터 점수 (0~1):    ", vector_scores)
print("BM25 점수 (0~수십):", bm25_scores)

# --- 나쁜 방법: 그냥 더하기 ---
naive = vector_scores + bm25_scores
print("\n-- 그냥 더하면 --")
print("합계:", np.round(naive, 2))
print("순위:", np.argsort(-naive), "<- BM25 크기에 완전히 지배된다")
print("벡터 1등(문서0)의 순위:", int(np.where(np.argsort(-naive) == 0)[0][0]) + 1, "위로 밀림")


# --- 방법 1: min-max 정규화 후 가중합 ---
def minmax(x, eps=1e-12):
    lo, hi = x.min(), x.max()
    return (x - lo) / max(hi - lo, eps)  # 전부 같은 값이면 0으로


ALPHA = 0.6  # 벡터 쪽 가중치
mm = ALPHA * minmax(vector_scores) + (1 - ALPHA) * minmax(bm25_scores)
print(f"\n-- min-max + 가중합 (alpha={ALPHA}) --")
print("점수:", np.round(mm, 4))
print("순위:", np.argsort(-mm))
print("  장점: 원래 점수 크기를 반영. 단점: 이상치 하나에 전체 스케일이 흔들린다.")


# --- 방법 2: z-score 정규화 ---
def zscore(x, eps=1e-12):
    return (x - x.mean()) / max(x.std(), eps)


z = ALPHA * zscore(vector_scores) + (1 - ALPHA) * zscore(bm25_scores)
print(f"\n-- z-score + 가중합 (alpha={ALPHA}) --")
print("점수:", np.round(z, 4))
print("순위:", np.argsort(-z))
print("  이상치에 min-max 보다 덜 민감하다.")


# --- 방법 3: RRF (Reciprocal Rank Fusion) ---
# 점수를 아예 버리고 순위만 쓴다. 스케일 문제가 원천적으로 없어서 실무 기본값으로 많이 쓴다.
def rrf(score_lists, k=60):
    """각 검색기의 점수 배열을 받아 RRF 점수를 반환. k는 상위 순위 가중을 조절."""
    n = len(score_lists[0])
    fused = np.zeros(n, dtype=np.float64)
    for scores in score_lists:
        order = np.argsort(-scores)  # 점수 내림차순 -> 문서 인덱스
        ranks = np.empty(n, dtype=np.int64)
        ranks[order] = np.arange(1, n + 1)  # 문서별 순위 (1부터)
        fused += 1.0 / (k + ranks)
    return fused


fused = rrf([vector_scores, bm25_scores])
print("\n-- RRF (k=60) --")
print("점수:", np.round(fused, 6))
print("순위:", np.argsort(-fused))
print("  점수 크기를 안 쓰므로 검색기 간 스케일 조정이 필요 없다.")

# --- 결과 비교 ---
print("\n-- 방법별 top-4 비교 --")
print(f"{'방법':<16}{'top-4'}")
for name, s in (
    ("벡터 단독", vector_scores),
    ("BM25 단독", bm25_scores),
    ("그냥 더하기", naive),
    ("min-max", mm),
    ("z-score", z),
    ("RRF", fused),
):
    print(f"{name:<16}{np.argsort(-s)[:4]}")

# --- 한쪽에만 등장하는 문서 처리 ---
# 실제로는 두 검색기가 서로 다른 문서 집합을 반환한다.
# 없는 문서는 '최하위 순위'로 채워야 한다. 0점으로 채우면 min-max 에서 왜곡된다.
print("\n-- 한쪽에만 있는 문서 --")
vec_hits = {0: 0.91, 2: 0.85, 5: 0.52}  # 벡터 검색 결과
bm25_hits = {1: 18.4, 5: 25.7, 6: 7.3}  # 키워드 검색 결과
all_ids = sorted(set(vec_hits) | set(bm25_hits))
print("합집합 문서:", all_ids)

n = len(all_ids)
fused2 = np.zeros(n)
for hits in (vec_hits, bm25_hits):
    # 해당 검색기에 없는 문서는 최하위(n+1) 순위로 취급
    ranked = sorted(hits, key=lambda d: -hits[d])
    rank_of = {d: i + 1 for i, d in enumerate(ranked)}
    for i, doc in enumerate(all_ids):
        fused2[i] += 1.0 / (60 + rank_of.get(doc, n + 1))

order = np.argsort(-fused2)
print("RRF 결과:", [(all_ids[i], round(float(fused2[i]), 6)) for i in order])
print("  문서5 가 1등: 두 검색기 모두에서 상위였기 때문 (교집합 가산점 효과)")
