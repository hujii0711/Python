"""01. 임베딩 배열의 기본 — shape / dtype / 메모리

RAG 에서 임베딩은 결국 (문서 수, 차원) 모양의 2차원 float 배열이다.
이 배열을 어떤 dtype 으로 들고 있느냐가 메모리와 속도를 그대로 결정한다.
"""

import numpy as np

rng = np.random.default_rng(0)

N, D = 5, 8  # 문서 5개, 차원 8 (실제로는 bge-m3 = 1024)
emb = rng.normal(size=(N, D)).astype(np.float32)

print("shape:", emb.shape)  # (문서 수, 차원)
print("dtype:", emb.dtype)
print("연속 메모리(C order):", emb.flags["C_CONTIGUOUS"])
print("전체 바이트:", emb.nbytes, "= 5 x 8 x 4")

# --- float32 vs float64 ---
# 임베딩 모델은 float32 로 내보낸다. float64 로 올리면 메모리만 2배 쓰고 이득이 없다.
print("\n-- dtype 별 메모리 (문서 100만개 x 1024차원) --")
for dtype in (np.float64, np.float32, np.float16):
    itemsize = np.dtype(dtype).itemsize
    gb = 1_000_000 * 1024 * itemsize / 1024**3
    print(f"  {np.dtype(dtype).name:8s} {itemsize}바이트/값 -> {gb:6.2f} GB")

# astype 은 항상 복사본을 만든다. 큰 배열에서는 이 복사 자체가 병목이 된다.
print("\nastype 은 복사:", np.shares_memory(emb, emb.astype(np.float64)))
print("같은 dtype 이면 copy=False 로 복사 회피 가능:", end=" ")
print(np.shares_memory(emb, emb.astype(np.float32, copy=False)))

# --- L2 정규화 ---
# 정규화해두면 코사인 유사도를 그냥 내적으로 계산할 수 있다 (02 예제 참고).
norms = np.linalg.norm(emb, axis=1, keepdims=True)  # (N, 1)
normalized = emb / norms

print("\n-- L2 정규화 --")
print("정규화 전 각 행의 크기:", np.round(norms.ravel(), 4))
print("정규화 후 각 행의 크기:", np.round(np.linalg.norm(normalized, axis=1), 4))

# axis / keepdims 를 빼먹는 것이 가장 흔한 실수다. 05 예제에서 자세히 다룬다.
print("\naxis=1 없이 norm 을 쓰면 스칼라가 나온다:", np.linalg.norm(emb).shape, "<- 전체 행렬의 norm")
