"""컬렉션 생성 및 접속 확인.

이미 컬렉션이 있으면 포인트만 비워서 깨끗한 상태로 만든다.
(로컬 모드의 delete_collection 은 Windows 에서 열려 있는 저장 파일 핸들 때문에
 디렉터리 삭제에 실패하고도 조용히 성공을 반환하므로 초기화 수단으로 쓰지 않는다.)
"""

from _client import COLLECTION, MODE, VECTOR_SIZE, get_client
from qdrant_client.models import Distance, Filter, FilterSelector, VectorParams

client = get_client()
print(f"mode={MODE}")

if client.collection_exists(COLLECTION):
    print(f"'{COLLECTION}' 컬렉션이 이미 있어서 포인트를 모두 비웁니다.")
    client.delete(
        collection_name=COLLECTION,
        points_selector=FilterSelector(filter=Filter()),
        wait=True,
    )
else:
    client.create_collection(
        collection_name=COLLECTION,
        vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
    )
    print(f"'{COLLECTION}' 컬렉션을 새로 만들었습니다.")

info = client.get_collection(COLLECTION)
print(f"  status      = {info.status}")
print(f"  points      = {client.count(COLLECTION).count}")
print(f"  vector size = {info.config.params.vectors.size}")
print(f"  distance    = {info.config.params.vectors.distance}")

# 로컬 모드는 파일 락을 쓰므로 명시적으로 닫아준다.
client.close()
