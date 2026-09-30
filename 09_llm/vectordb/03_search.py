"""유사도 검색 + payload 필터 검색."""

from _client import COLLECTION, encode, get_client
from qdrant_client.models import FieldCondition, Filter, MatchValue

client = get_client()
query = "리스트 순서를 거꾸로 만들고 싶어요"
query_vector = encode([query])[0].tolist()

print(f"[query] {query}\n")

print("-- 전체 검색 top 3 --")
for point in client.query_points(
    collection_name=COLLECTION,
    query=query_vector,
    limit=3,
    with_payload=True,
).points:
    print(
        f"  {point.score:.4f}  {point.payload['text']}  ({point.payload['category']})"
    )

print("\n-- category='pandas' 필터 top 3 --")
for point in client.query_points(
    collection_name=COLLECTION,
    query=query_vector,
    query_filter=Filter(
        must=[FieldCondition(key="category", match=MatchValue(value="pandas"))]
    ),
    limit=3,
    with_payload=True,
).points:
    print(
        f"  {point.score:.4f}  {point.payload['text']}  ({point.payload['category']})"
    )

client.close()
