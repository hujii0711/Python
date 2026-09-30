"""문서를 임베딩해서 Qdrant에 저장(upsert)."""

from _client import COLLECTION, encode, get_client
from qdrant_client.models import PointStruct

DOCS = [
    ("파이썬에서 리스트를 뒤집는 방법", "python"),
    ("list reverse in python", "python"),
    ("판다스로 CSV 파일 읽기", "pandas"),
    ("DataFrame 결측치 채우기", "pandas"),
    ("오늘 날씨가 좋네요", "daily"),
    ("점심으로 김치찌개를 먹었다", "daily"),
]

client = get_client()
texts = [text for text, _ in DOCS]
vectors = encode(texts)
print(f"임베딩 완료: {vectors.shape}")

points = [
    PointStruct(
        id=idx,
        vector=vector.tolist(),
        payload={"text": text, "category": category},
    )
    for idx, (vector, (text, category)) in enumerate(zip(vectors, DOCS))
]

client.upsert(collection_name=COLLECTION, points=points, wait=True)
print(f"저장 완료: {client.count(COLLECTION).count} points")

client.close()
