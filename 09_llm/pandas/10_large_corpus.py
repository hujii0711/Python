"""10. 대용량 코퍼스 — 스트리밍 / parquet / dtype 최적화

문서 수백만 건을 한 번에 메모리에 올릴 수 없다.
chunksize 로 흘려보내고, parquet 로 저장하고, dtype 을 줄인다.
"""

import io
import tempfile
import time
from pathlib import Path

import numpy as np
import pandas as pd

rng = np.random.default_rng(0)

# --- 테스트용 코퍼스 생성 ---
N = 100_000
categories = ["python", "pandas", "numpy", "fastapi", "qdrant"]
corpus = pd.DataFrame(
    {
        "chunk_id": [f"C{i:07d}" for i in range(N)],
        "doc_id": [f"D{i // 5:06d}" for i in range(N)],
        "category": rng.choice(categories, N),
        "lang": rng.choice(["ko", "en"], N),
        "n_tokens": rng.integers(20, 512, N),
        "views": rng.integers(0, 10_000, N),
        "text": ["이것은 테스트용 청크 본문입니다. 검색 대상이 되는 텍스트입니다."] * N,
    }
)

tmpdir = Path(tempfile.mkdtemp(prefix="rag_corpus_"))
print(f"청크 {N:,}건, 작업 경로: {tmpdir}")

# --- 1) dtype 최적화 ---
print("\n-- dtype 최적화 --")


def mb(df):
    return df.memory_usage(deep=True).sum() / 1024**2


before = mb(corpus)
optimized = corpus.copy()
optimized["category"] = optimized["category"].astype("category")  # 종류 5개
optimized["lang"] = optimized["lang"].astype("category")  # 종류 2개
optimized["n_tokens"] = optimized["n_tokens"].astype("int16")  # 최대 512
optimized["views"] = optimized["views"].astype("int32")  # 최대 1만

print(f"  최적화 전: {before:7.2f} MB")
print(f"  최적화 후: {mb(optimized):7.2f} MB  ({(1 - mb(optimized) / before):.1%} 절감)")
print("\n컬럼별 메모리 (MB):")
per_col = (optimized.memory_usage(deep=True) / 1024**2).round(3).sort_values(ascending=False)
print(per_col.to_string())
print("  -> text 컬럼이 대부분을 차지한다. 반복되는 짧은 문자열이면 category 도 고려할 만하다.")

# 범위를 넘으면 조용히 잘린다. 반드시 최대값을 먼저 확인할 것.
print("\n-- dtype 축소 함정 --")
small = pd.Series([1000], dtype="int64")
print(f"  int64 1000 -> int8 변환: {small.astype('int8').iloc[0]} <- 오버플로, 에러 없음")
print(f"  안전 확인: max={small.max()}, int8 상한={np.iinfo(np.int8).max}")

# --- 2) CSV vs parquet ---
print("\n-- 저장 포맷 비교 --")
csv_path = tmpdir / "corpus.csv"
pq_path = tmpdir / "corpus.parquet"

t0 = time.perf_counter()
corpus.to_csv(csv_path, index=False)
t_csv_w = time.perf_counter() - t0

t0 = time.perf_counter()
optimized.to_parquet(pq_path, index=False)
t_pq_w = time.perf_counter() - t0

t0 = time.perf_counter()
_ = pd.read_csv(csv_path)
t_csv_r = time.perf_counter() - t0

t0 = time.perf_counter()
pq_back = pd.read_parquet(pq_path)
t_pq_r = time.perf_counter() - t0

comp = pd.DataFrame(
    {
        "크기(MB)": [csv_path.stat().st_size / 1024**2, pq_path.stat().st_size / 1024**2],
        "쓰기(s)": [t_csv_w, t_pq_w],
        "읽기(s)": [t_csv_r, t_pq_r],
    },
    index=["csv", "parquet"],
)
print(comp.round(3).to_string())
print("\n  parquet 은 dtype 을 보존한다. CSV 는 읽을 때마다 다시 추론해야 한다:")
print(f"    parquet 왕복 후 category dtype: {pq_back['category'].dtype}")
print(f"    csv     왕복 후 category dtype: {pd.read_csv(csv_path)['category'].dtype}")

# --- 3) 컬럼만 골라 읽기 (parquet 의 진짜 장점) ---
t0 = time.perf_counter()
few = pd.read_parquet(pq_path, columns=["chunk_id", "category", "views"])
t_cols = time.perf_counter() - t0
print(f"\n-- 필요한 컬럼만 읽기 --")
print(f"  전체 {len(pq_back.columns)}컬럼: {t_pq_r:.3f}s, {mb(pq_back):.2f} MB")
print(f"  3컬럼만        : {t_cols:.3f}s, {mb(few):.2f} MB")
print("  -> 무거운 text 컬럼을 건너뛸 수 있다. CSV 는 불가능하다.")

# --- 4) chunksize 스트리밍 ---
# 파일 전체를 메모리에 올리지 않고 조각으로 처리한다.
# 실전에서는 이 루프 안에서 임베딩하고 벡터DB 에 upsert 한다.
print("\n-- chunksize 스트리밍 집계 --")
CHUNKSIZE = 20_000
cat_counts = pd.Series(dtype="int64")
total_tokens = 0
n_batches = 0

for batch in pd.read_csv(csv_path, chunksize=CHUNKSIZE, usecols=["category", "n_tokens"]):
    cat_counts = cat_counts.add(batch["category"].value_counts(), fill_value=0)
    total_tokens += int(batch["n_tokens"].sum())
    n_batches += 1

print(f"  배치 {n_batches}개 x {CHUNKSIZE:,}행 처리 (한 번에 올린 메모리는 배치 1개분)")
print("  카테고리별 청크 수:")
print(cat_counts.astype(int).sort_index().to_string())
print(f"  총 토큰 수: {total_tokens:,}")

# 전체를 올려 계산한 결과와 일치하는지 검증
assert total_tokens == int(corpus["n_tokens"].sum())
print(f"  전체 로딩 결과와 일치: {total_tokens == int(corpus['n_tokens'].sum())}")

# --- 5) 임베딩 배치 루프 패턴 ---
print("\n-- 실전 패턴: 스트리밍 + 배치 임베딩 --")
BATCH = 32
processed = 0
for batch in pd.read_csv(csv_path, chunksize=CHUNKSIZE, usecols=["chunk_id", "text"]):
    # 임베딩 모델은 한 번에 BATCH 개씩 넣는 게 효율적이다
    for start in range(0, len(batch), BATCH):
        sub = batch.iloc[start : start + BATCH]
        # vectors = encode(sub["text"].tolist())   # 실제로는 여기서 임베딩
        # client.upsert(COLLECTION, points=[...])  # 그리고 바로 적재
        processed += len(sub)
    if processed >= 40_000:  # 예제라서 일부만
        break
print(f"  {processed:,}건 처리 (실제로는 encode + upsert 가 들어간다)")
print("  파일 -> chunksize 배치 -> 임베딩 배치 -> upsert 로 2단 분할하는 게 정석이다.")

# --- 6) 진행 상황을 재개 가능하게 ---
# 수백만 건 적재는 중간에 끊긴다. 어디까지 했는지 남겨야 한다.
print("\n-- 재개 가능하게 만들기 --")
done_path = tmpdir / "done_ids.parquet"
pd.DataFrame({"chunk_id": corpus["chunk_id"].head(40_000)}).to_parquet(done_path, index=False)

done = set(pd.read_parquet(done_path)["chunk_id"])
remaining = corpus[~corpus["chunk_id"].isin(done)]
print(f"  완료 {len(done):,}건 기록 -> 남은 작업 {len(remaining):,}건")
print("  isin 으로 이미 처리한 id 를 건너뛴다. 중복 임베딩 비용을 막는다.")

# 정리
for f in tmpdir.iterdir():
    f.unlink()
tmpdir.rmdir()
print(f"\n임시 파일 정리 완료: {not tmpdir.exists()}")
