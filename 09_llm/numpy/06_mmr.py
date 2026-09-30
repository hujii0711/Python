"""06. MMR (Maximal Marginal Relevance) — 검색 결과의 다양성 확보

단순 top-k 는 거의 같은 내용의 청크를 여러 개 가져온다.
LLM 컨텍스트가 중복으로 낭비되므로, 관련성과 다양성을 함께 본다.

    MMR = argmax [ lambda * sim(q, d) - (1 - lambda) * max sim(d, 이미 뽑은 것) ]
"""

import numpy as np

rng = np.random.default_rng(0)


def l2_normalize(x, axis=-1, eps=1e-12):
    return x / np.maximum(np.linalg.norm(x, axis=axis, keepdims=True), eps)


# --- 실제 RAG 에서 문제가 되는 상황을 만든다 ---
# 핵심은 "여러 주제가 모두 쿼리와 관련 있는데, 각 주제 안에 거의 같은 청크가 여럿"인 경우다.
# 주제 하나만 관련 있는 코퍼스를 만들면 MMR 이 무관한 문서를 끌어오는 것처럼 보여서
# 예제로 부적절하다.
D = 32
query = l2_normalize(rng.normal(size=D))

# 쿼리와의 유사도는 비슷하게(0.70~0.78) 두고, 주제끼리는 서로 다른 방향을 향하게 만든다.
ALPHAS = (0.78, 0.74, 0.70)  # 각 주제 중심이 쿼리와 갖는 코사인
docs, labels = [], []
for topic, alpha in enumerate(ALPHAS):
    # 쿼리와 직교하는 성분을 뽑는다 (그램-슈미트)
    u = rng.normal(size=D)
    u -= (u @ query) * query
    u = l2_normalize(u)
    center = alpha * query + np.sqrt(1 - alpha**2) * u
    for copy in range(4):
        # 노이즈를 작게 줘서 '거의 중복인 청크 4개'를 만든다
        docs.append(center + rng.normal(scale=0.06, size=D))
        labels.append(f"주제{topic}-{copy}")
docs = l2_normalize(np.array(docs, dtype=np.float32), axis=1)
query = query.astype(np.float32)

sim_to_query = docs @ query  # (N,)
sim_between = docs @ docs.T  # (N, N) 문서 간 유사도


def mmr(sim_to_query, sim_between, k, lambda_=0.5):
    """MMR 로 k개를 순차 선택한다. 반환값은 선택된 인덱스 리스트."""
    selected = []
    candidates = list(range(len(sim_to_query)))

    for _ in range(k):
        if not selected:
            # 첫 개는 관련성만 본다
            best = max(candidates, key=lambda i: sim_to_query[i])
        else:
            # 이미 뽑은 것들과의 최대 유사도를 벌점으로 쓴다
            redundancy = sim_between[np.ix_(candidates, selected)].max(axis=1)
            score = lambda_ * sim_to_query[candidates] - (1 - lambda_) * redundancy
            best = candidates[int(np.argmax(score))]
        selected.append(best)
        candidates.remove(best)

    return selected


K = 5

print("-- 코퍼스 구성 확인 --")
print("  주제별 쿼리 유사도:", {
    f"주제{t}": round(float(sim_to_query[t * 4 : t * 4 + 4].mean()), 3) for t in range(3)
})
print(f"  같은 주제 내 청크끼리 유사도: {sim_between[0, 1]:.3f} <- 거의 중복")
print(f"  다른 주제 청크와의 유사도   : {sim_between[0, 4]:.3f}")

plain = np.argsort(-sim_to_query)[:K]

print("\n-- 단순 top-5 (관련성만) --")
for i in plain:
    print(f"  {labels[i]:12s} sim={sim_to_query[i]:.4f}")
print("  선택된 주제:", sorted({labels[i].split('-')[0] for i in plain}))

for lam in (0.7, 0.3):
    picked = mmr(sim_to_query, sim_between, K, lambda_=lam)
    print(f"\n-- MMR (lambda={lam}) --")
    for i in picked:
        print(f"  {labels[i]:12s} sim={sim_to_query[i]:.4f}")
    print("  선택된 주제:", sorted({labels[i].split('-')[0] for i in picked}))

print("\nlambda 가 1에 가까우면 관련성만(=단순 top-k), 0에 가까우면 다양성만 본다.")

# --- 실전 팁: 전체가 아니라 1차 검색 결과에만 적용한다 ---
# 문서 간 유사도 행렬은 N^2 이라 전체 코퍼스에 쓸 수 없다.
for n in (50, 1_000, 100_000):
    gb = n * n * 4 / 1024**3
    print(f"  문서 간 유사도 행렬 N={n:>7,} -> {gb:9.4f} GB")
print("  -> 벡터DB 로 top-50 정도 받아온 뒤 그 안에서만 MMR 을 돌리는 게 정석이다.")
