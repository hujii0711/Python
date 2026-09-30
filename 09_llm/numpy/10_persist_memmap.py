"""10. 벡터 저장과 memmap — 메모리에 다 안 올리고 검색하기

임베딩 재계산은 비싸다. 한 번 만들면 디스크에 저장해두고 재사용한다.
코퍼스가 RAM 보다 크면 memmap 으로 필요한 부분만 읽는다.
"""

import tempfile
from pathlib import Path

import numpy as np

rng = np.random.default_rng(0)


def l2_normalize(x, axis=-1, eps=1e-12):
    return x / np.maximum(np.linalg.norm(x, axis=axis, keepdims=True), eps)


N, D, K = 10_000, 128, 5
docs = l2_normalize(rng.normal(size=(N, D)).astype(np.float32), axis=1)
doc_ids = np.array([f"doc-{i:05d}" for i in range(N)])
query = l2_normalize(rng.normal(size=D).astype(np.float32))

# 임시 디렉터리에서 작업한다 (실제로는 프로젝트 안의 고정 경로를 쓸 것)
tmpdir = Path(tempfile.mkdtemp(prefix="rag_vectors_"))
print("작업 경로:", tmpdir)

# --- 1) .npy — 배열 하나 ---
npy = tmpdir / "embeddings.npy"
np.save(npy, docs)
loaded = np.load(npy)
print(f"\n-- .npy --")
print(f"  크기: {npy.stat().st_size / 1024:.1f} KB")
print(f"  왕복 후 동일: {np.array_equal(docs, loaded)}, dtype 유지: {loaded.dtype}")

# --- 2) .npz — 여러 배열을 함께 (id 와 벡터를 같이 보관) ---
npz = tmpdir / "index.npz"
np.savez(npz, embeddings=docs, ids=doc_ids)
with np.load(npz, allow_pickle=False) as z:
    print(f"\n-- .npz --")
    print(f"  담긴 키: {z.files}")
    print(f"  ids 예시: {z['ids'][:3]}")
    print(f"  크기: {npz.stat().st_size / 1024:.1f} KB")

# 압축본. 정규화된 float32 임베딩은 거의 안 줄어든다 (랜덤에 가까운 비트라서).
npz_c = tmpdir / "index_compressed.npz"
np.savez_compressed(npz_c, embeddings=docs, ids=doc_ids)
ratio = npz_c.stat().st_size / npz.stat().st_size
print(f"  압축본: {npz_c.stat().st_size / 1024:.1f} KB (원본의 {ratio:.1%})")
print("  -> 임베딩은 압축 이득이 거의 없다. 로드만 느려지니 보통 비압축을 쓴다.")

# --- 3) mmap_mode='r' — 파일을 메모리에 올리지 않고 열기 ---
mm = np.load(npy, mmap_mode="r")
print(f"\n-- np.load(mmap_mode='r') --")
print(f"  타입: {type(mm).__name__}, shape: {mm.shape}")
print("  이 시점에 RAM 으로 읽은 데이터는 없다. 접근하는 부분만 페이지 단위로 올라온다.")

# 슬라이스하면 그 부분만 읽힌다
block = mm[:100]
print(f"  mm[:100] -> {block.shape}, memmap 인가: {isinstance(block, np.memmap)}")

# --- 4) memmap 위에서 청크 검색 ---
# 전체를 RAM 에 올리지 않고 top-k 를 구한다.
def search_memmap(path, query, k, chunk_size=2048):
    data = np.load(path, mmap_mode="r")
    n = data.shape[0]
    best_idx = np.zeros(0, dtype=np.int64)
    best_score = np.zeros(0, dtype=np.float32)

    for start in range(0, n, chunk_size):
        block = np.asarray(data[start : start + chunk_size])  # 이 청크만 RAM 으로
        scores = block @ query
        take = min(k, scores.shape[0])
        top = np.argpartition(-scores, take - 1)[:take]
        best_idx = np.concatenate([best_idx, top + start])
        best_score = np.concatenate([best_score, scores[top]])
        keep = np.argsort(-best_score)[:k]
        best_idx, best_score = best_idx[keep], best_score[keep]

    return best_idx, best_score


idx_mm, score_mm = search_memmap(npy, query, K)

# 전체를 올려서 계산한 결과와 비교
full = docs @ query
idx_full = np.argsort(-full)[:K]

print(f"\n-- memmap 청크 검색 vs 전체 로드 --")
print(f"  memmap : {idx_mm} / {np.round(score_mm, 5)}")
print(f"  전체   : {idx_full} / {np.round(full[idx_full], 5)}")
print(f"  일치   : {np.array_equal(idx_mm, idx_full)}")
print(f"  청크 하나당 RAM: {2048 * D * 4 / 1024:.0f} KB (전체 {docs.nbytes / 1024:.0f} KB 대신)")

# --- 5) memmap 은 읽기 전용으로 열 것 ---
print("\n-- 쓰기 주의 --")
try:
    mm[0, 0] = 1.0
except ValueError as exc:
    print(f"  mmap_mode='r' 은 쓰기 불가: {exc}")
print("  mode='r+' 로 열면 디스크 파일이 직접 바뀐다. 인덱스가 조용히 오염되므로 기본은 'r'.")

# --- 6) Windows 함정: memmap 이 파일 핸들을 쥐고 있다 ---
# 열려 있는 동안에는 파일을 지우거나 덮어쓸 수 없다.
# 인덱스를 재생성하는 배치 작업에서 실제로 걸리는 문제다.
print("\n-- Windows 함정: 열린 memmap 은 파일을 잠근다 --")
try:
    npy.unlink()
    print("  삭제 성공 (Linux/macOS 는 열려 있어도 unlink 가 된다)")
except PermissionError as exc:
    print(f"  PermissionError: WinError {exc.winerror} — 다른 프로세스가 파일을 사용 중")
    print("  해결: memmap 을 가리키는 모든 참조를 없애야 핸들이 닫힌다.")

# block 도 mm 과 같은 mmap 을 참조하는 뷰다. 둘 다 없애야 한다.
del block
del mm
print("  del 로 참조 해제 후 삭제:", end=" ")
npy.unlink()
print("성공")

# --- 7) 신규 문서 추가는 append 가 안 된다 ---
# .npy 는 append 를 지원하지 않는다. 증분 업데이트가 필요하면 벡터DB(Qdrant)를 쓰는 게 맞다.
print("\n-- 한계 --")
print("  .npy 는 append 불가. 문서 추가 시 전체를 다시 써야 한다.")
print("  필터링/증분 갱신/동시 접근이 필요하면 ../vectordb 의 Qdrant 를 쓸 것.")
print("  numpy 파일은 '임베딩 캐시'나 '오프라인 평가'용으로 적합하다.")

# 정리
for f in tmpdir.iterdir():
    f.unlink()
tmpdir.rmdir()
print(f"\n임시 파일 정리 완료: {not tmpdir.exists()}")
