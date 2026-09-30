"""04. 메타데이터 필터링 — 검색 범위를 좁히기

RAG 에서 "2026년 이후 python 카테고리 문서만" 같은 조건은 거의 필수다.
pandas 에서 필터를 검증한 뒤, 같은 조건을 벡터DB payload 필터로 옮기는 흐름을 본다.
"""

import pandas as pd

chunks = pd.DataFrame(
    {
        "chunk_id": [f"C{i:02d}" for i in range(10)],
        "doc_id": ["D1", "D1", "D2", "D2", "D3", "D3", "D4", "D4", "D5", "D5"],
        "category": pd.Categorical(
            ["python", "python", "pandas", "pandas", "python", "python", "etc", "etc", "pandas", "pandas"]
        ),
        "lang": ["ko", "ko", "ko", "en", "ko", "en", "ko", "ko", "en", "en"],
        "published": pd.to_datetime(
            ["2025-06-01", "2025-06-01", "2026-01-15", "2026-01-15",
             "2026-03-20", "2026-03-20", "2024-11-02", "2024-11-02",
             "2026-05-10", "2026-05-10"]
        ),
        "views": [120, 120, 890, 890, 1500, 1500, 30, 30, 640, 640],
        "is_public": [True, True, True, True, True, True, False, False, True, True],
    }
)

print("-- 전체 청크 --")
print(chunks.to_string(index=False))

# --- 1) boolean mask ---
mask = (chunks["category"] == "python") & (chunks["published"] >= "2026-01-01")
print(f"\n-- mask: python & 2026년 이후 -> {mask.sum()}건 --")
print(chunks.loc[mask, ["chunk_id", "category", "published"]].to_string(index=False))

# 흔한 실수: and / or 를 쓰면 에러가 난다. 반드시 & | 와 괄호를 쓸 것.
try:
    chunks[(chunks["category"] == "python") and (chunks["views"] > 100)]
except ValueError as exc:
    print(f"\nand 사용 시: ValueError - {str(exc)[:60]}...")
print("  -> & 를 쓰고 각 조건을 괄호로 감쌀 것")

# --- 2) query() — 조건이 길어지면 읽기 쉽다 ---
q = chunks.query("category == 'python' and views > 100 and is_public")
print(f"\n-- query(): {len(q)}건 --")
print(q[["chunk_id", "category", "views"]].to_string(index=False))

# 외부 변수는 @ 로 참조한다
min_views = 500
q2 = chunks.query("views >= @min_views and lang == 'ko'")
print(f"\nquery + @변수 (views>={min_views}, ko): {q2['chunk_id'].tolist()}")

# --- 3) isin / between ---
print("\n-- isin / between --")
print("카테고리 isin:", chunks[chunks["category"].isin(["python", "pandas"])]["chunk_id"].tolist())
print(
    "날짜 between :",
    chunks[chunks["published"].between("2026-01-01", "2026-04-01")]["chunk_id"].tolist(),
)

# --- 4) 날짜 접근자 ---
chunks["year"] = chunks["published"].dt.year
chunks["month"] = chunks["published"].dt.month
print("\n-- 연도별 청크 수 --")
print(chunks["year"].value_counts().sort_index().to_string())

# --- 5) 필터 조건을 Qdrant payload 필터로 옮기기 ---
# pandas 에서 조건을 검증하고 나면, 같은 의미의 payload 필터를 만들면 된다.
print("\n-- pandas 조건 -> Qdrant Filter 대응 --")
mapping = pd.DataFrame(
    [
            ("df['category'] == 'python'", "FieldCondition(key='category', match=MatchValue(value='python'))"),
            ("df['category'].isin([...])", "FieldCondition(key='category', match=MatchAny(any=[...]))"),
            ("df['views'] >= 500", "FieldCondition(key='views', range=Range(gte=500))"),
            ("df['published'] >= '2026-01-01'", "FieldCondition(key='published', range=DatetimeRange(gte=...))"),
            ("A & B", "Filter(must=[A, B])"),
            ("A | B", "Filter(should=[A, B])"),
            ("~A", "Filter(must_not=[A])"),
    ],
    columns=["pandas", "Qdrant"],
)
print(mapping.to_string(index=False))

# --- 6) 필터가 후보를 얼마나 줄이는지 미리 확인 ---
# 필터가 너무 좁으면 top-k 를 채우지 못한다. 임베딩 전에 여기서 점검하는 게 싸다.
print("\n-- 조건별 남는 청크 수 --")
conditions = {
    "전체": pd.Series(True, index=chunks.index),
    "is_public": chunks["is_public"],
    "+ 2026년 이후": chunks["is_public"] & (chunks["year"] >= 2026),
    "+ ko": chunks["is_public"] & (chunks["year"] >= 2026) & (chunks["lang"] == "ko"),
    "+ python": chunks["is_public"] & (chunks["year"] >= 2026) & (chunks["lang"] == "ko")
    & (chunks["category"] == "python"),
}
for name, cond in conditions.items():
    n = int(cond.sum())
    bar = "#" * n
    print(f"  {name:16s} {n:2d}건 {bar}")
print("  -> 마지막 조건은 top-5 를 채울 수 없다. 필터를 완화하거나 fallback 이 필요하다.")

# --- 7) category dtype 주의 ---
print("\n-- category dtype --")
print("메모리: category", chunks["category"].memory_usage(deep=True), "bytes")
print("        str     ", chunks["category"].astype("str").memory_usage(deep=True), "bytes")
# groupby 에서 쓰지 않는 카테고리도 나오려면 observed=False 를 명시해야 한다 (3.0 기본값은 True)
print("\ngroupby 기본(observed=True) 결과 행 수:", len(chunks.groupby("category").size()))
