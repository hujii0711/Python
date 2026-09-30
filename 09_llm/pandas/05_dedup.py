"""05. 중복 제거 — 같은 내용이 여러 번 검색되는 걸 막기

중복 청크는 임베딩 비용을 낭비하고, 검색 결과에서 LLM 컨텍스트를 먹는다.
정확 중복부터 정규화 중복, 근사 중복까지 단계적으로 걸러낸다.
"""

import hashlib

import pandas as pd

df = pd.DataFrame(
    {
        "chunk_id": [f"C{i:02d}" for i in range(9)],
        "doc_id": ["D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8", "D9"],
        "text": [
            "리스트를 뒤집는 방법은 reversed() 입니다.",
            "리스트를 뒤집는 방법은 reversed() 입니다.",  # 완전 동일
            "리스트를 뒤집는  방법은  reversed() 입니다.",  # 공백만 다름
            "리스트를 뒤집는 방법은 REVERSED() 입니다.",  # 대소문자만 다름
            "리스트를 뒤집는 방법은 reversed() 입니다!",  # 문장부호만 다름
            "판다스로 CSV 를 읽습니다.",
            "판다스로 CSV 를 읽습니다.",  # 완전 동일
            "DataFrame 의 결측치를 채웁니다.",
            "이 문서는 저작권 안내입니다. 무단 복제를 금합니다.",  # 보일러플레이트
        ],
        "views": [100, 50, 30, 20, 10, 800, 400, 300, 5],
    }
)
print(f"-- 원본 {len(df)}건 --")
print(df[["chunk_id", "text"]].to_string(index=False))

# --- 1) 정확 중복 ---
print("\n-- 1) 정확 중복 (drop_duplicates) --")
dup_mask = df.duplicated(subset=["text"], keep=False)
print("중복 그룹에 속한 청크:", df.loc[dup_mask, "chunk_id"].tolist())

# keep 옵션에 따라 무엇을 남길지 결정된다
exact = df.drop_duplicates(subset=["text"], keep="first")
print(f"keep='first': {len(df)} -> {len(exact)}건, 남은 id {exact['chunk_id'].tolist()}")

# 더 나은 방법: 조회수가 높은 쪽(원본일 가능성이 큰 쪽)을 남긴다
best = df.sort_values("views", ascending=False).drop_duplicates(subset=["text"], keep="first")
best = best.sort_index()
print(f"views 높은 쪽 유지: 남은 id {best['chunk_id'].tolist()}")

# --- 2) 정규화 후 중복 ---
# 공백/대소문자/문장부호 차이는 의미가 같으므로 정규화 키로 묶는다.
print("\n-- 2) 정규화 후 중복 --")
norm = (
    df["text"]
    .str.lower()
    .str.replace(r"[^\w\s]", "", regex=True)  # 문장부호 제거
    .str.replace(r"\s+", " ", regex=True)  # 공백 정규화
    .str.strip()
)
df["norm_key"] = norm
print(df[["chunk_id", "norm_key"]].to_string(index=False))

groups = df.groupby("norm_key", sort=False)["chunk_id"].agg(list)
print("\n정규화 키로 묶인 그룹:")
for key, ids in groups.items():
    flag = "  <- 중복" if len(ids) > 1 else ""
    print(f"  {ids} : {key[:38]!r}{flag}")

deduped = df.drop_duplicates(subset=["norm_key"], keep="first")
print(f"\n정규화 중복 제거: {len(df)} -> {len(deduped)}건 (정확 중복만으로는 {len(exact)}건)")

# --- 3) 해시로 중복 관리 ---
# 텍스트 전체를 비교하는 대신 해시를 저장하면 메모리와 조인 비용이 줄고,
# 벡터DB payload 에 넣어두면 재적재 시 중복 판정을 바로 할 수 있다.
print("\n-- 3) 해시 --")
df["text_hash"] = df["norm_key"].map(lambda s: hashlib.sha256(s.encode()).hexdigest()[:12])
print(df[["chunk_id", "text_hash"]].to_string(index=False))
print("\n해시 기준 중복 수:", int(df.duplicated(subset=["text_hash"]).sum()))
print("  -> 증분 적재 시 '이미 있는 해시인지'만 확인하면 된다")

# --- 4) 보일러플레이트 탐지 ---
# 저작권/푸터처럼 여러 문서에 반복되는 문구는 검색에 방해가 된다.
# 실제 코퍼스에서는 '같은 텍스트가 N개 이상의 문서에 등장'으로 찾는다.
print("\n-- 4) 보일러플레이트 --")
doc_counts = df.groupby("norm_key")["doc_id"].nunique().sort_values(ascending=False)
print("텍스트별 등장 문서 수:")
print(doc_counts.head(3).to_string())
BOILER_MIN_DOCS = 2
boiler = doc_counts[doc_counts >= BOILER_MIN_DOCS].index
print(f"\n{BOILER_MIN_DOCS}개 이상 문서에 등장 -> 보일러플레이트 후보 {len(boiler)}건")

# --- 5) 근사 중복 후보 좁히기 ---
# 완전 일치가 아닌 '비슷한' 중복은 임베딩 유사도로 봐야 한다(numpy 06 MMR 참고).
# 다만 전수 비교는 N^2 이므로, pandas 단계에서 길이로 후보를 좁히면 크게 줄어든다.
print("\n-- 5) 근사 중복 후보 좁히기 --")
df["n_chars"] = df["text"].str.len()
df["len_bucket"] = (df["n_chars"] // 10) * 10  # 10자 단위 버킷
bucket_sizes = df.groupby("len_bucket").size()
print("길이 버킷별 청크 수:")
print(bucket_sizes.to_string())
total_pairs = len(df) * (len(df) - 1) // 2
bucket_pairs = int((bucket_sizes * (bucket_sizes - 1) // 2).sum())
print(f"\n전수 비교 쌍: {total_pairs}  /  같은 버킷끼리만: {bucket_pairs}")
print("  -> 길이가 많이 다르면 근사 중복일 수 없으므로 비교 대상에서 빼도 안전하다")

# --- 6) 최종 파이프라인 ---
# 순서가 중요하다: 정규화 -> 해시 -> (조회수 높은 쪽 유지) 중복 제거 -> 보일러플레이트 제외
print("\n-- 최종 파이프라인 --")
final = (
    df.sort_values("views", ascending=False)  # 남길 우선순위를 먼저 정한다
    .drop_duplicates(subset=["text_hash"], keep="first")
    .loc[lambda d: ~d["norm_key"].isin(boiler)]  # 보일러플레이트 제외
    .sort_index()  # 원래 순서 복구
)
print(f"{len(df)}건 -> {len(final)}건")
print(final[["chunk_id", "doc_id", "views", "text"]].to_string(index=False))
print("\n제거된 청크:", sorted(set(df['chunk_id']) - set(final['chunk_id'])))
print("  sort_values 를 먼저 하지 않으면 keep='first' 가 '조회수 높은 쪽'이 아니라")
print("  '먼저 나온 쪽'을 남긴다. 순서가 결과를 바꾼다.")
