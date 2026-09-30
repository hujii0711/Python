"""04. 배치 검색과 메모리 — 행렬곱 한 번 vs 청크 분할

쿼리 M개 x 문서 N개 점수 행렬은 M*N 크기다. 그냥 만들면 메모리가 터진다.
청크로 쪼개면 결과는 같고 메모리 상한은 내가 정한다.
"""

import numpy as np

rng = np.random.default_rng(0)


def l2_normalize(x, axis=-1):
    return x / np.linalg.norm(x, axis=axis, keepdims=True)


M, N, D, K = 8, 20_000, 128, 5
queries = l2_normalize(rng.normal(size=(M, D)).astype(np.float32), axis=1)
docs = l2_normalize(rng.normal(size=(N, D)).astype(np.float32), axis=1)

# --- 점수 행렬 메모리 추정 ---
print("-- 점수 행렬 크기 (float32) --")
for m, n in ((8, 20_000), (100, 1_000_000), (1000, 10_000_000)):
    gb = m * n * 4 / 1024**3
    print(f"  쿼리 {m:>5,} x 문서 {n:>12,} -> {gb:9.2f} GB")
print("  -> 큰 코퍼스에서는 전체 행렬을 만들 수 없다.")


def topk(scores, k):
    """(M, N) 점수에서 행별 top-k 인덱스와 점수를 정렬된 상태로 반환."""
    part = np.argpartition(-scores, k, axis=1)[:, :k]
    order = np.argsort(-np.take_along_axis(scores, part, axis=1), axis=1)
    idx = np.take_along_axis(part, order, axis=1)
    return idx, np.take_along_axis(scores, idx, axis=1)


# --- 방법 1: 한 번에 ---
full_scores = queries @ docs.T  # (M, N)
idx_full, score_full = topk(full_scores, K)
print(f"\n한 번에: {queries.shape} @ {docs.T.shape} -> {full_scores.shape}")


# --- 방법 2: 문서를 청크로 나눠서 ---
def search_chunked(queries, docs, k, chunk_size):
    """문서를 chunk_size 씩 읽어 점수 상위 k개만 유지한다.

    메모리는 (M, chunk_size) 로 제한된다. 각 청크의 top-k 만 모아
    마지막에 다시 top-k 를 뽑는 방식(부분 결과 병합)이다.
    """
    m = queries.shape[0]
    best_scores = np.full((m, 0), -np.inf, dtype=np.float32)
    best_idx = np.zeros((m, 0), dtype=np.int64)

    for start in range(0, docs.shape[0], chunk_size):
        block = docs[start : start + chunk_size]
        scores = queries @ block.T  # (M, chunk)
        take = min(k, scores.shape[1])
        idx, sc = topk(scores, take)
        # 청크 내 인덱스를 전체 인덱스로 보정
        best_idx = np.concatenate([best_idx, idx + start], axis=1)
        best_scores = np.concatenate([best_scores, sc], axis=1)
        # 누적된 후보에서 다시 상위 k개만 남긴다
        keep = np.argsort(-best_scores, axis=1)[:, :k]
        best_idx = np.take_along_axis(best_idx, keep, axis=1)
        best_scores = np.take_along_axis(best_scores, keep, axis=1)

    return best_idx, best_scores


CHUNK = 4096
idx_chunk, score_chunk = search_chunked(queries, docs, K, CHUNK)
peak_mb = M * CHUNK * 4 / 1024**2
print(f"청크({CHUNK})로: 한 번에 올리는 점수 행렬 = ({M}, {CHUNK}) = {peak_mb:.2f} MB")

# --- 두 방법의 결과가 같은지 검증 ---
print("\n-- 결과 검증 --")
print("인덱스 동일:", np.array_equal(idx_full, idx_chunk))
print("점수   동일:", np.allclose(score_full, score_chunk))

print("\n-- 쿼리별 top-5 --")
for i in range(M):
    pairs = ", ".join(f"{d}:{s:.4f}" for d, s in zip(idx_full[i], score_full[i]))
    print(f"  쿼리{i}: {pairs}")

# float32 로 계산하면 float64 대비 메모리 절반, 속도는 보통 더 빠르다.
print("\n-- dtype 확인 --")
print("float32 입력 -> 결과 dtype:", (queries @ docs.T).dtype)
print("float64 로 섞이면:", (queries.astype(np.float64) @ docs.T).dtype, "<- 메모리 2배")
