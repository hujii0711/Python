"""03. Top-K 추출 — argsort vs argpartition

검색은 "가장 비슷한 k개"만 필요하다. 전체를 정렬하는 건 낭비다.
argpartition 은 k번째 경계만 맞춰놓고 나머지는 정렬하지 않아 O(N) 이다.
"""

import time

import numpy as np

rng = np.random.default_rng(0)

N = 500_000  # 문서 50만개
K = 5
scores = rng.random(N).astype(np.float32)  # 유사도 점수라고 가정

# --- 방법 1: 전체 정렬 (O(N log N)) ---
t0 = time.perf_counter()
idx_sort = np.argsort(-scores)[:K]  # 내림차순 정렬 후 앞에서 K개
t_sort = time.perf_counter() - t0

# --- 방법 2: argpartition (O(N)) ---
t0 = time.perf_counter()
part = np.argpartition(-scores, K)[:K]  # 상위 K개를 앞으로 몰아준다 (순서는 보장 안 됨)
idx_part = part[np.argsort(-scores[part])]  # 그 K개만 다시 정렬
t_part = time.perf_counter() - t0

print(f"문서 {N:,}개에서 top-{K}")
print(f"  argsort      : {t_sort * 1000:7.2f} ms -> {idx_sort}")
print(f"  argpartition : {t_part * 1000:7.2f} ms -> {idx_part}")
print(f"  결과 동일    : {np.array_equal(idx_sort, idx_part)}")
print(f"  속도 차이    : {t_sort / t_part:.1f}배")

# --- argpartition 의 함정 ---
# argpartition 만 쓰면 상위 K개가 '모여있을 뿐' 정렬되어 있지 않다.
raw = np.argpartition(-scores, K)[:K]
print("\n-- argpartition 직후는 정렬되지 않음 --")
print("  점수:", np.round(scores[raw], 5), "<- 내림차순이 아니다")
print("  정렬:", np.round(scores[idx_part], 5), "<- 한 번 더 정렬해야 한다")

# --- 여러 쿼리를 한 번에 (axis 지정) ---
M = 4
score_matrix = rng.random((M, 1000)).astype(np.float32)  # 쿼리 4개 x 문서 1000개

part = np.argpartition(-score_matrix, K, axis=1)[:, :K]  # (M, K)
# 각 행별로 다시 정렬한다. take_along_axis 로 행마다 다른 인덱스를 적용.
row_scores = np.take_along_axis(score_matrix, part, axis=1)
order = np.argsort(-row_scores, axis=1)
topk_idx = np.take_along_axis(part, order, axis=1)
topk_scores = np.take_along_axis(score_matrix, topk_idx, axis=1)

print(f"\n-- 쿼리 {M}개 동시 top-{K} --")
for i in range(M):
    pairs = ", ".join(f"{d}:{s:.4f}" for d, s in zip(topk_idx[i], topk_scores[i]))
    print(f"  쿼리{i}: {pairs}")

# 검증: 첫 쿼리를 단독으로 계산해도 같아야 한다
solo = np.argsort(-score_matrix[0])[:K]
print("\n첫 쿼리 단독 계산과 일치:", np.array_equal(solo, topk_idx[0]))

# K 가 N 에 가까우면 argsort 가 낫다. argpartition 의 이득은 K << N 일 때 나온다.
print(f"\n참고: K({K}) << N({N:,}) 일 때만 argpartition 이 유리하다.")
