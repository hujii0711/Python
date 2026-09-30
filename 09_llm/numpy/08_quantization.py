"""08. 벡터 양자화 — 메모리를 줄이고 재현율을 지키기

문서 100만개 x 1024차원 float32 = 3.8GB. 이걸 줄이는 두 가지 방법.
  - int8 스칼라 양자화: 4배 절감, 재현율 거의 유지
  - binary(1bit) 양자화: 32배 절감, 재현율 손실. 후보 추리기용으로 쓴다.
"""

import numpy as np

rng = np.random.default_rng(0)


def l2_normalize(x, axis=-1, eps=1e-12):
    return x / np.maximum(np.linalg.norm(x, axis=axis, keepdims=True), eps)


N, D, K = 5_000, 256, 10

# 실제 임베딩은 완전 랜덤이 아니라 주제별로 뭉쳐 있다(군집 구조).
# 순수 랜덤 가우시안으로 만들면 고차원에서 벡터가 거의 직교해 top-1 유사도가 0.2 수준으로
# 뭉개지고, 양자화 재현율이 실제보다 훨씬 나쁘게 나온다.
# 아래 설정의 top-1 코사인은 약 0.73 으로, 실제 임베딩(0.7~0.9)과 비슷한 수준이다.
N_TOPIC, NOISE = 50, 0.7
centers = rng.normal(size=(N_TOPIC, D))  # 정규화하지 않는다(성분 크기를 노이즈와 맞추기 위해)
topic_of = rng.integers(0, N_TOPIC, size=N)
docs = l2_normalize(
    (centers[topic_of] + NOISE * rng.normal(size=(N, D))).astype(np.float32), axis=1
)
q_topic = rng.integers(0, N_TOPIC, size=20)
queries = l2_normalize(
    (centers[q_topic] + NOISE * rng.normal(size=(20, D))).astype(np.float32), axis=1
)

# 정답(float32 그대로 계산한 top-k)
exact = np.argsort(-(queries @ docs.T), axis=1)[:, :K]


def recall_at_k(approx, exact):
    """정답 top-k 중 몇 개를 다시 찾아냈는지 (순서는 보지 않음)."""
    hits = [len(set(a) & set(e)) for a, e in zip(approx, exact)]
    return np.mean(hits) / exact.shape[1]


# --- int8 스칼라 양자화 ---
# 벡터별로 최대 절댓값을 스케일로 잡고 -127~127 정수로 매핑한다.
def quantize_int8(x):
    scale = np.abs(x).max(axis=1, keepdims=True) / 127.0
    q = np.round(x / np.maximum(scale, 1e-12)).astype(np.int8)
    return q, scale.astype(np.float32)


q_docs, doc_scale = quantize_int8(docs)
q_queries, query_scale = quantize_int8(queries)

# int8 끼리 내적하면 int32 로 누적된다. 그 뒤 스케일을 되돌린다.
# astype(np.int32) 를 빼면 int8 오버플로로 값이 망가진다.
int_dot = q_queries.astype(np.int32) @ q_docs.astype(np.int32).T
int8_scores = int_dot * query_scale * doc_scale.T
int8_topk = np.argsort(-int8_scores, axis=1)[:, :K]

# --- binary(1bit) 양자화 ---
# 부호만 남긴다. 양수 -> 1, 음수 -> 0. 유사도는 해밍 거리로 본다.
def quantize_binary(x):
    return np.packbits(x > 0, axis=1)  # (N, D) bool -> (N, D/8) uint8


b_docs = quantize_binary(docs)
b_queries = quantize_binary(queries)

# XOR 후 1의 개수 = 해밍 거리. 거리가 작을수록 유사하다.
# numpy 2.0+ 의 bitwise_count 가 없으면 unpackbits 로 대체한다.
if hasattr(np, "bitwise_count"):
    def hamming(a, b):
        return np.bitwise_count(a[:, None, :] ^ b[None, :, :]).sum(axis=2)
else:
    def hamming(a, b):
        xor = a[:, None, :] ^ b[None, :, :]
        return np.unpackbits(xor, axis=2).sum(axis=2)


ham = hamming(b_queries, b_docs)
binary_topk = np.argsort(ham, axis=1)[:, :K]  # 거리는 오름차순

# --- 메모리 비교 ---
print("-- 메모리 (문서 100만개 x 1024차원) --")
for name, bytes_per_val in (("float32", 4), ("int8", 1), ("binary(1bit)", 1 / 8)):
    gb = 1_000_000 * 1024 * bytes_per_val / 1024**3
    print(f"  {name:14s} {gb:7.3f} GB  ({4 / bytes_per_val:5.1f}배 절감)")

print(f"\n-- 이 예제 실측 (문서 {N:,} x {D}차원) --")
print(f"  float32 : {docs.nbytes / 1024:8.1f} KB")
print(f"  int8    : {q_docs.nbytes / 1024:8.1f} KB (+ scale {doc_scale.nbytes / 1024:.1f} KB)")
print(f"  binary  : {b_docs.nbytes / 1024:8.1f} KB")

print(f"\n-- 데이터 현실성 확인 --")
print(f"  top-1 코사인 평균: {(queries @ docs.T).max(axis=1).mean():.3f} (실제 임베딩은 0.7~0.9)")

print(f"\n-- 재현율 (recall@{K}, float32 결과 대비) --")
print(f"  int8                : {recall_at_k(int8_topk, exact):.3f}  <- 그대로 써도 된다")
print(f"  binary 단독         : {recall_at_k(binary_topk, exact):.3f}  <- 최종 순위에는 쓸 수 없다")

# --- 실전 패턴: binary 로 후보를 넓게 추리고 float32 로 재채점 ---
# binary 단독 재현율이 낮은 이유: 256비트로는 정보가 너무 적어 해밍 거리 동점이 쏟아진다.
# 하지만 '정답이 후보 안에 들어오는지'는 잘 맞춘다. 그래서 넓게 추린 뒤 재채점하면 회복된다.
# Qdrant 의 binary quantization + oversampling/rescore 도 정확히 이 구조다.
print(f"\n-- binary 후보 추리기 + float32 재채점 --")
for rescore_n in (20, 100, 500):
    cand = np.argsort(ham, axis=1)[:, :rescore_n]
    rescored = np.empty((queries.shape[0], K), dtype=np.int64)
    for i in range(queries.shape[0]):
        c = cand[i]
        s = docs[c] @ queries[i]  # 후보만 float32 로 다시 계산
        rescored[i] = c[np.argsort(-s)[:K]]
    cost = rescore_n / N * 100
    print(f"  후보 {rescore_n:>3}개 재채점: {recall_at_k(rescored, exact):.3f}  (전체 계산의 {cost:4.1f}%)")
print("  -> 메모리는 32배 줄이고 재현율은 거의 그대로. 후보 개수가 정확도/비용 손잡이다.")

# --- int8 오버플로: 이건 반드시 알아야 한다 ---
# numpy 는 int8 @ int8 을 int8 로 누적한다. 자동으로 int32 로 승격해주지 않는다.
# 256차원 내적이면 127*127*256 까지 누적되므로 int8(-128~127) 은 한참 전에 넘친다.
# 에러가 나지 않고 값만 조용히 망가지는 게 위험한 지점이다.
print("\n-- int8 내적에서 astype(int32) 를 빼면 --")
small_q, small_d = q_queries[:1], q_docs[:3]
bad = small_q @ small_d.T
good = small_q.astype(np.int32) @ small_d.astype(np.int32).T
print("  int8 그대로 :", bad.dtype, bad.ravel())
print("  int32 승격  :", good.dtype, good.ravel())
print("  값 일치:", np.array_equal(bad, good), "<- 오버플로로 값이 완전히 다르다")
print("  반드시 astype(np.int32) 를 먼저 할 것. 에러 없이 틀린 점수가 나온다.")
