"""06. 임베딩 결과와 DataFrame 정렬 — 가장 위험한 단계

임베딩은 numpy 배열, 메타데이터는 DataFrame 이다.
이 둘을 행 순서로 맞추는데, 중간에 정렬/필터가 끼면 조용히 어긋난다.
에러가 안 나고 "엉뚱한 문서가 검색되는" 증상으로만 나타난다.
"""

import numpy as np
import pandas as pd

rng = np.random.default_rng(0)

df = pd.DataFrame(
    {
        "chunk_id": ["C0", "C1", "C2", "C3", "C4"],
        "text": ["파이썬 리스트", "판다스 CSV", "넘파이 배열", "Qdrant 검색", "FastAPI 서버"],
        "views": [10, 500, 300, 50, 900],
    }
)
D = 4
emb = rng.normal(size=(len(df), D)).astype(np.float32)
emb = emb / np.linalg.norm(emb, axis=1, keepdims=True)

print("-- 시작 상태 (행 순서가 일치) --")
for i, row in enumerate(df.itertuples()):
    print(f"  행{i} {row.chunk_id} {row.text:12s} emb[{i}]={np.round(emb[i], 3)}")

# --- 사고 1: 정렬 후 임베딩을 그대로 쓴다 ---
print("\n-- 사고 1: sort_values 후 임베딩 미정렬 --")
sorted_df = df.sort_values("views", ascending=False)
print("정렬된 DataFrame:")
print(sorted_df[["chunk_id", "views"]].to_string(index=False))
print("정렬 후 인덱스:", sorted_df.index.tolist(), "<- 원래 위치를 기억하고 있다")
print("\n이 상태에서 emb[0] 을 sorted_df 첫 행의 벡터로 쓰면:")
print(f"  sorted_df 첫 행 = {sorted_df.iloc[0]['chunk_id']} 인데 emb[0] 은 {df.iloc[0]['chunk_id']} 의 벡터")
print("  -> 완전히 다른 문서의 벡터를 쓰게 된다. 에러는 안 난다.")

# 올바른 방법: 인덱스로 임베딩도 같이 재배열한다
aligned = emb[sorted_df.index.to_numpy()]
print("\n올바르게 정렬:")
for i, row in enumerate(sorted_df.itertuples()):
    orig = df.index.get_loc(row.Index)
    ok = np.allclose(aligned[i], emb[orig])
    print(f"  {row.chunk_id} -> emb[{orig}] 사용, 일치: {ok}")

# --- 사고 2: 필터 후 인덱스가 비연속이 된다 ---
print("\n-- 사고 2: 필터 후 비연속 인덱스 --")
filtered = df[df["views"] >= 300]
print("필터 결과 인덱스:", filtered.index.tolist(), "<- 0,1,2 가 아니다")
print("emb[filtered.index] 는 올바르지만, reset_index 후에는 다르다:")
reset = filtered.reset_index(drop=True)
print("  reset_index(drop=True) 인덱스:", reset.index.tolist())
print("  -> 이제 원래 위치 정보가 사라졌다. reset 전에 임베딩을 먼저 슬라이스해야 한다.")

correct = emb[filtered.index.to_numpy()]
print(f"\n올바른 순서: 먼저 emb[filtered.index] -> shape {correct.shape}, 그 다음 reset_index")

# --- 안전한 패턴 1: 원래 위치를 컬럼으로 박아둔다 ---
print("\n-- 안전한 패턴 1: row_pos 컬럼 --")
df2 = df.copy()
df2["row_pos"] = np.arange(len(df2))  # 임베딩 배열의 행 번호
after = df2.sort_values("views", ascending=False).query("views >= 300").reset_index(drop=True)
vectors = emb[after["row_pos"].to_numpy()]  # 어떤 변형을 거쳐도 안전하다
print(after[["chunk_id", "views", "row_pos"]].to_string(index=False))
print("정렬/필터/reset 을 모두 거친 뒤에도 매칭 정확:",
      all(np.allclose(vectors[i], emb[p]) for i, p in enumerate(after["row_pos"])))

# --- 안전한 패턴 2: merge 로 명시적 조인 ---
print("\n-- 안전한 패턴 2: merge --")
emb_df = pd.DataFrame({"chunk_id": df["chunk_id"], "row_pos": np.arange(len(df))})
merged = after[["chunk_id", "views"]].merge(emb_df, on="chunk_id", how="left", validate="1:1")
print(merged.to_string(index=False))
print("validate='1:1' 이 중복 키를 잡아준다:")
try:
    dup = pd.DataFrame({"chunk_id": ["C0", "C0"], "row_pos": [0, 1]})
    after[["chunk_id"]].merge(dup, on="chunk_id", validate="1:1")
except pd.errors.MergeError as exc:
    print(f"  MergeError: {exc}")

# --- 벡터를 DataFrame 안에 담는 건 어떨까 ---
print("\n-- 벡터를 컬럼에 담으면? --")
obj_df = df.copy()
obj_df["vector"] = list(emb)  # 각 셀이 ndarray
print("dtype:", obj_df["vector"].dtype, "<- object. 행별로 따로 저장된다")
print(f"메모리: object 컬럼 {obj_df['vector'].memory_usage(deep=True):,} bytes")
print(f"        연속 배열   {emb.nbytes:,} bytes")
print("정렬은 같이 따라가서 편하지만:")
print("  - 행렬곱을 하려면 np.stack 으로 매번 다시 모아야 한다")
print("  - 연속 메모리가 아니라 검색이 느리다")
stacked = np.stack(obj_df["vector"].to_numpy())
print(f"  np.stack 후: {stacked.shape}, 원본과 동일: {np.allclose(stacked, emb)}")
print("\n결론: 메타데이터는 DataFrame, 벡터는 별도 ndarray.")
print("      둘을 잇는 건 row_pos 컬럼이나 id 기준 merge 로 명시한다.")
