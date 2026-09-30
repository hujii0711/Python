"""05. 정규화에서 실제로 터지는 함정들

RAG 에서 검색이 조용히 망가지는 대표 원인. 에러가 안 나고 점수만 틀리는 게 무섭다.
"""

import numpy as np

rng = np.random.default_rng(0)
emb = rng.normal(size=(4, 6)).astype(np.float32)

# --- 함정 1: axis 를 빼먹는다 ---
print("-- 함정 1: axis 누락 --")
wrong = emb / np.linalg.norm(emb)  # 전체 행렬의 norm 하나로 나눔
right = emb / np.linalg.norm(emb, axis=1, keepdims=True)
print("axis 없음 -> 각 행의 크기:", np.round(np.linalg.norm(wrong, axis=1), 4), "<- 1이 아니다")
print("axis=1    -> 각 행의 크기:", np.round(np.linalg.norm(right, axis=1), 4))

# --- 함정 2: keepdims 를 빼먹는다 ---
print("\n-- 함정 2: keepdims 누락 --")
norms_flat = np.linalg.norm(emb, axis=1)  # (4,)
norms_keep = np.linalg.norm(emb, axis=1, keepdims=True)  # (4, 1)
print("keepdims=False shape:", norms_flat.shape, "-> (4,6) / (4,) 는 브로드캐스팅 실패")
try:
    emb / norms_flat
except ValueError as exc:
    print("  ValueError:", exc)
print("keepdims=True  shape:", norms_keep.shape, "-> 정상")
# norms_flat[:, None] 로도 같은 효과를 낼 수 있다
print("  [:, None] 로도 가능:", np.allclose(emb / norms_flat[:, None], right))

# --- 함정 3: 0 벡터 → 0으로 나누기 ---
# 빈 문자열이나 공백만 있는 청크를 임베딩하면 0에 가까운 벡터가 나올 수 있다.
print("\n-- 함정 3: 영벡터 --")
with_zero = np.vstack([emb, np.zeros((1, 6), dtype=np.float32)])
with np.errstate(invalid="ignore", divide="ignore"):
    naive = with_zero / np.linalg.norm(with_zero, axis=1, keepdims=True)
print("마지막 행:", naive[-1], "<- nan")
print("nan 개수:", np.isnan(naive).sum())
print("nan 이 섞이면 이후 모든 점수가 nan 이 되고, argmax 결과도 망가진다:")
q = np.ones(6, dtype=np.float32) / np.sqrt(6)
print("  점수:", np.round(naive @ q, 4), "-> argmax:", np.nanargmax(naive @ q), "(nanargmax 필요)")


def safe_normalize(x, axis=-1, eps=1e-12):
    """0 벡터를 0 벡터로 남겨두는 안전한 정규화."""
    norm = np.linalg.norm(x, axis=axis, keepdims=True)
    return x / np.maximum(norm, eps)


safe = safe_normalize(with_zero, axis=1)
print("safe_normalize -> nan 개수:", np.isnan(safe).sum())
print("  영벡터 행:", safe[-1], "-> 점수 0.0 (검색에서 자연히 밀린다)")

# --- 함정 4: in-place 연산이 원본을 바꾼다 ---
print("\n-- 함정 4: in-place --")
original = emb.copy()
view = emb  # 복사가 아니다. 같은 배열을 가리킨다
view /= np.linalg.norm(view, axis=1, keepdims=True)  # /= 는 제자리 수정
print("원본이 바뀌었는가:", not np.allclose(emb, original), "<- 캐시해둔 임베딩이 오염된다")
emb = original  # 복구

# --- 함정 5: 정수 배열에 나누기 ---
print("\n-- 함정 5: 정수 dtype --")
int_vec = np.array([[3, 4]], dtype=np.int32)
print("int32 배열 나누기 결과 dtype:", (int_vec / np.linalg.norm(int_vec)).dtype, "(float64 로 승격)")
print("  -> float32 로 유지하려면 미리 astype(np.float32) 할 것")

# --- 함정 6: 이미 정규화된 것을 또 정규화 ---
# 멱등이므로 무해하지만, 매 검색마다 하면 순수 낭비다. 저장 시점에 한 번만.
once = safe_normalize(emb, axis=1)
twice = safe_normalize(once, axis=1)
print("\n-- 함정 6: 중복 정규화 --")
print("멱등인가:", np.allclose(once, twice), "(무해하지만 검색 경로에서는 낭비)")
