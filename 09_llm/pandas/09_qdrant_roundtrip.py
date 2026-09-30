"""09. DataFrame <-> Qdrant 왕복 — payload 매핑

적재: DataFrame 행 -> PointStruct(id, vector, payload)
검색: 결과 -> DataFrame 으로 되돌려 pandas 로 후처리

접속 설정은 ../vectordb/_client.py 를 재사용한다 (QDRANT_MODE 환경변수 적용).
이 예제는 전용 컬렉션 'pandas_demo' 를 쓰고 끝나면 지운다.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "vectordb"))

from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    Range,
    VectorParams,
)

from _client import MODE, VECTOR_SIZE, encode, get_client

COLLECTION = "pandas_demo"

df = pd.DataFrame(
    {
        "chunk_id": ["C1", "C2", "C3", "C4", "C5", "C6"],
        "doc_id": ["D1", "D1", "D2", "D2", "D3", "D3"],
        "text": [
            "파이썬에서 리스트를 뒤집는 방법",
            "리스트 슬라이싱으로 역순 만들기",
            "판다스로 CSV 파일 읽기",
            "DataFrame 의 결측치를 채우는 방법",
            "넘파이 배열의 브로드캐스팅",
            "행렬곱으로 유사도 계산하기",
        ],
        "category": ["python", "python", "pandas", "pandas", "numpy", "numpy"],
        "views": [1200, 340, 890, 450, 700, 1500],
        "published": pd.to_datetime(
            ["2026-01-15", "2026-02-03", "2026-02-20", "2026-03-01", "2026-03-11", "2026-04-02"]
        ),
    }
)
print(f"mode={MODE}, 청크 {len(df)}건")
print(df[["chunk_id", "category", "views", "text"]].to_string(index=False))

client = get_client()
if client.collection_exists(COLLECTION):
    client.delete_collection(COLLECTION)
client.create_collection(
    COLLECTION, vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE)
)

# --- 1) DataFrame -> payload ---
# Timestamp 는 JSON 으로 직렬화되지 않는다. 문자열이나 정수로 바꿔야 한다.
payload_df = df.drop(columns=["text"]).copy()
payload_df["published"] = payload_df["published"].dt.strftime("%Y-%m-%d")
payload_df["text"] = df["text"]  # 원문도 payload 에 넣어두면 검색 후 바로 쓸 수 있다

print("\n-- payload 로 쓸 컬럼 dtype --")
print(payload_df.dtypes.to_string())

# to_dict('records') 가 행 단위 dict 리스트를 만든다. 이게 payload 형식과 바로 맞는다.
payloads = payload_df.to_dict("records")
print("\n첫 payload:", payloads[0])

# numpy 스칼라는 직렬화 문제를 일으킬 수 있으므로 타입을 확인한다
print("views 값의 타입:", type(payloads[0]["views"]).__name__)

# --- 2) 임베딩 후 upsert ---
vectors = encode(df["text"].tolist())
print(f"\n임베딩 완료: {vectors.shape}")

points = [
    PointStruct(id=i, vector=vec.tolist(), payload=pl)
    for i, (vec, pl) in enumerate(zip(vectors, payloads))
]
client.upsert(COLLECTION, points=points, wait=True)
print(f"적재 완료: {client.count(COLLECTION).count} points")

# --- 3) 검색 결과 -> DataFrame ---
query = "리스트 순서를 거꾸로 만들고 싶어요"
hits = client.query_points(
    COLLECTION, query=encode([query])[0].tolist(), limit=6, with_payload=True
).points


def hits_to_frame(hits):
    """Qdrant 검색 결과를 DataFrame 으로. payload 를 컬럼으로 펼친다."""
    return pd.DataFrame(
        [{"point_id": h.id, "score": h.score, **(h.payload or {})} for h in hits]
    )


res = hits_to_frame(hits)
res["rank"] = range(1, len(res) + 1)
print(f"\n-- 검색: {query!r} --")
print(res[["rank", "chunk_id", "category", "score", "text"]].round(4).to_string(index=False))

# --- 4) 받아온 결과를 pandas 로 후처리 ---
# 문서 단위 집계 (08 예제와 같은 패턴)
doc_agg = res.groupby("doc_id", as_index=False).agg(
    best_score=("score", "max"), n_chunks=("chunk_id", "count")
).sort_values("best_score", ascending=False)
print("\n-- 문서별 집계 --")
print(doc_agg.round(4).to_string(index=False))

# --- 5) 서버 필터 vs pandas 필터 ---
# 같은 조건을 두 곳에 걸 수 있는데, 결과가 다르다.
# limit 을 작게 잡아야 차이가 드러난다. limit 이 전체 건수만큼 크면 둘이 같아 보인다.
LIMIT = 2
qvec = encode([query])[0].tolist()
cond = "views >= 500"

# (a) 서버에서 필터 -> 조건을 통과한 것들 중에서 top-LIMIT 을 채운다
server_df = hits_to_frame(
    client.query_points(
        COLLECTION,
        query=qvec,
        query_filter=Filter(must=[FieldCondition(key="views", range=Range(gte=500))]),
        limit=LIMIT,
        with_payload=True,
    ).points
)

# (b) 먼저 top-LIMIT 을 받고 pandas 에서 필터 -> 받은 것 중 조건 미달은 사라진다
raw = hits_to_frame(client.query_points(COLLECTION, query=qvec, limit=LIMIT, with_payload=True).points)
client_df = raw.query(cond)

print(f"\n-- 서버 필터 vs pandas 필터 (limit={LIMIT}, 조건: {cond}) --")
print(f"  (a) 서버 필터        : {server_df['chunk_id'].tolist()}  -> {len(server_df)}건")
print(f"  (b) 받은 뒤 pandas   : {client_df['chunk_id'].tolist()}  -> {len(client_df)}건")
print(f"      (b)가 먼저 받은 것: {raw['chunk_id'].tolist()} (views={raw['views'].tolist()})")
print(f"\n  같은 limit 인데 결과 수가 다르다: {len(server_df)}건 vs {len(client_df)}건")
print("  (b)는 조건 미달인 C2 가 top-2 한 자리를 차지해버려 남는 게 줄어든다.")
print("  조건이 더 좁거나 limit 이 더 작으면 아예 0건이 될 수도 있다.")
print("  -> 필터는 반드시 서버(query_filter)에서 걸 것. pandas 는 그 뒤 후처리용.")

# --- 6) 전체를 DataFrame 으로 덤프 (scroll) ---
# 적재 내용 검증이나 오프라인 평가용으로 전체를 내려받는다.
records, offset = [], None
while True:
    batch, offset = client.scroll(COLLECTION, limit=4, offset=offset, with_payload=True)
    records.extend({"point_id": p.id, **(p.payload or {})} for p in batch)
    if offset is None:
        break

dump = pd.DataFrame(records).sort_values("point_id")
print(f"\n-- scroll 로 전체 덤프: {len(dump)}건 --")
print(dump[["point_id", "chunk_id", "category", "views"]].to_string(index=False))

# 적재 전 DataFrame 과 일치하는지 검증
check = dump.sort_values("chunk_id")["chunk_id"].tolist() == sorted(df["chunk_id"])
print("적재 전 DataFrame 과 chunk_id 일치:", check)

# published 는 문자열로 넣었으므로 다시 datetime 으로 되돌려야 한다
dump["published"] = pd.to_datetime(dump["published"])
print("복원한 published dtype:", dump["published"].dtype)

# 정리
client.delete_collection(COLLECTION)
client.close()
print(f"\n'{COLLECTION}' 컬렉션 삭제 완료")
