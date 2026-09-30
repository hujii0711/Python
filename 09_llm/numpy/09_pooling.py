"""09. 풀링 — 토큰 -> 문장, 청크 -> 문서

임베딩 모델 내부에서 토큰 벡터를 하나로 합치는 게 풀링이다.
패딩을 빼먹는 것이 여기서 가장 흔하고 조용한 버그다.
"""

import numpy as np

rng = np.random.default_rng(0)

B, T, H = 3, 6, 8  # 문장 3개, 최대 토큰 6개, 은닉 차원 8
token_emb = rng.normal(size=(B, T, H)).astype(np.float32)

# 실제 토큰 길이가 다르므로 패딩이 들어간다. 1 = 실제 토큰, 0 = 패딩.
mask = np.array(
    [
        [1, 1, 1, 1, 0, 0],  # 4 토큰
        [1, 1, 0, 0, 0, 0],  # 2 토큰
        [1, 1, 1, 1, 1, 1],  # 6 토큰
    ],
    dtype=np.float32,
)
print("토큰 임베딩 shape:", token_emb.shape, "(문장, 토큰, 차원)")
print("실제 토큰 수:", mask.sum(axis=1).astype(int))

# --- 틀린 mean pooling: 패딩까지 평균에 넣는다 ---
wrong = token_emb.mean(axis=1)  # (B, H)

# --- 맞는 mean pooling: 마스크로 가중 평균 ---
# mask 를 (B, T, 1) 로 늘려 곱하고, 실제 토큰 수로 나눈다.
m = mask[:, :, None]  # (B, T, 1)
right = (token_emb * m).sum(axis=1) / np.maximum(m.sum(axis=1), 1e-9)

print("\n-- mean pooling --")
print("차이의 크기 (문장별):", np.round(np.linalg.norm(wrong - right, axis=1), 4))
print("  3번째 문장은 패딩이 없어서 차이가 0:", np.allclose(wrong[2], right[2]))
print("  패딩 비율이 큰 2번째 문장이 가장 많이 틀어진다.")

# 이 버그는 에러 없이 통과하고, 짧은 문장일수록 임베딩이 0 쪽으로 끌려간다.
print("\n패딩 포함 평균의 노름:", np.round(np.linalg.norm(wrong, axis=1), 4))
print("마스크 적용 평균의 노름:", np.round(np.linalg.norm(right, axis=1), 4))

# --- max pooling: 패딩을 -inf 로 만들어야 한다 ---
masked = np.where(m > 0, token_emb, -np.inf)
max_pooled = masked.max(axis=1)
naive_max = token_emb.max(axis=1)  # 패딩 값이 최대일 수 있다
print("\n-- max pooling --")
print("마스크 없이 == 마스크 적용:", np.allclose(naive_max, max_pooled))
print("  (패딩 위치 값이 우연히 최대면 틀어진다)")

# --- CLS 풀링: 첫 토큰만 쓴다 ---
cls_pooled = token_emb[:, 0, :]
print("\n-- CLS 풀링 --", cls_pooled.shape, "(BERT 계열의 기본. 첫 토큰만)")

# --- 청크 -> 문서 단위 집계 ---
# 긴 문서를 여러 청크로 쪼개 임베딩했다면, 문서 점수를 하나로 합쳐야 한다.
print("\n-- 청크 점수를 문서 점수로 --")
chunk_doc_id = np.array([0, 0, 0, 1, 1, 2, 2, 2, 2])  # 청크 9개 -> 문서 3개
chunk_scores = np.array([0.91, 0.42, 0.38, 0.55, 0.88, 0.30, 0.29, 0.31, 0.33], dtype=np.float32)
n_docs = chunk_doc_id.max() + 1

# max: 가장 잘 맞는 청크 하나로 문서를 대표 (RAG 에서 보통 이걸 쓴다)
doc_max = np.full(n_docs, -np.inf, dtype=np.float32)
np.maximum.at(doc_max, chunk_doc_id, chunk_scores)

# mean: 문서 전체가 고르게 관련된 경우에 유리
doc_sum = np.zeros(n_docs, dtype=np.float32)
np.add.at(doc_sum, chunk_doc_id, chunk_scores)
doc_count = np.bincount(chunk_doc_id, minlength=n_docs)
doc_mean = doc_sum / doc_count

print("청크 점수 :", chunk_scores)
print("문서 id   :", chunk_doc_id)
print("max 집계  :", np.round(doc_max, 4), "-> 순위", np.argsort(-doc_max))
print("mean 집계 :", np.round(doc_mean, 4), "-> 순위", np.argsort(-doc_mean))
print("  문서2 는 청크가 4개지만 전부 낮아서 mean 에서 더 불리하다.")
print("  max 는 '한 군데라도 정답이 있으면' 뽑히므로 QA 형태의 RAG 에 잘 맞는다.")

# bincount 로 문서별 청크 수를 세는 것도 자주 쓴다
print("\n문서별 청크 수:", doc_count)
