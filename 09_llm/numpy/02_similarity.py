"""02. 유사도 계산 — 코사인 / 내적 / 유클리드

RAG 검색의 핵심 연산. 셋의 관계를 알면 불필요한 계산을 줄일 수 있다.
"""

import numpy as np

rng = np.random.default_rng(0)

D = 16
query = rng.normal(size=D).astype(np.float32)
docs = rng.normal(size=(6, D)).astype(np.float32)


def l2_normalize(x, axis=-1):
    return x / np.linalg.norm(x, axis=axis, keepdims=True)


# --- 1) 코사인 유사도: 정의대로 ---
cos_raw = (docs @ query) / (np.linalg.norm(docs, axis=1) * np.linalg.norm(query))

# --- 2) 미리 정규화해두면 그냥 내적 ---
# RAG 에서는 이 방식을 쓴다. 문서 벡터는 저장할 때 한 번만 정규화하면 되므로
# 검색 때마다 norm 을 다시 계산하지 않는다. (Qdrant 의 Cosine distance 도 내부적으로 동일)
q_n = l2_normalize(query)
docs_n = l2_normalize(docs, axis=1)
cos_dot = docs_n @ q_n

print("-- 코사인 유사도 --")
print("정의대로 :", np.round(cos_raw, 6))
print("정규화+내적:", np.round(cos_dot, 6))
print("같은 값인가:", np.allclose(cos_raw, cos_dot, atol=1e-6))

# --- 3) 유클리드 거리와의 관계 ---
# 단위 벡터끼리는 ||a-b||^2 = 2 - 2*cos(a,b)
# 즉 코사인 내림차순 = 유클리드 거리 오름차순. 순위가 완전히 같다.
euclid = np.linalg.norm(docs_n - q_n, axis=1)
print("\n-- 유클리드 거리 (정규화된 벡터) --")
print("거리        :", np.round(euclid, 6))
print("2-2cos 의 제곱근:", np.round(np.sqrt(2 - 2 * cos_dot), 6))
print("코사인 내림차순 순위:", np.argsort(-cos_dot))
print("거리   오름차순 순위:", np.argsort(euclid), "<- 동일")

# --- 4) 브로드캐스팅: 쿼리 1개 대 문서 N개 ---
# docs_n @ q_n 이 이미 (N,) 를 만든다. 루프가 필요 없다.
print("\n-- 1:N --", docs_n.shape, "@", q_n.shape, "->", (docs_n @ q_n).shape)

# --- 5) 행렬곱: 쿼리 M개 대 문서 N개 ---
queries = l2_normalize(rng.normal(size=(3, D)).astype(np.float32), axis=1)
scores = queries @ docs_n.T  # (M, N)
print("-- M:N --", queries.shape, "@", docs_n.T.shape, "->", scores.shape)
print("쿼리별 최고 점수 문서:", scores.argmax(axis=1))

# 내적은 벡터 크기에 영향을 받는다. 정규화하지 않으면 '긴' 벡터가 유리해진다.
long_doc = docs[0] * 5  # 방향은 같고 크기만 5배
print("\n-- 정규화를 빼먹으면 --")
print(f"원본 내적     : {docs[0] @ query:.4f}")
print(f"5배 벡터 내적 : {long_doc @ query:.4f}  <- 방향이 같은데 점수가 5배")
print(f"코사인(원본)  : {cos_dot[0]:.4f}")
print(f"코사인(5배)   : {l2_normalize(long_doc) @ q_n:.4f}  <- 동일. 크기에 무관")
