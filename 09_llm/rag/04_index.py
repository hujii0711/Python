"""4단계: 색인.

로드 → 청킹 → 임베딩 결과를 Qdrant 컬렉션에 넣는다.
QdrantVectorStore.add_documents 가 임베딩 호출과 저장을 함께 처리한다.

포인트 id 를 "문서 경로 + 청크 번호" 로 고정하기 때문에 이 스크립트를 여러 번
실행해도 중복이 쌓이지 않고 같은 자리에 덮어써진다.
`--reset` 을 주면 기존 포인트를 모두 비우고 처음부터 색인한다.
"""

import importlib
import sys
from collections import Counter
from pathlib import Path

from _config import (
    COLLECTION,
    MODE,
    ensure_collection,
    get_client,
    get_vector_store,
    make_point_id,
    setup_console,
)
from qdrant_client.models import Filter, FilterSelector

chunking = importlib.import_module("02_chunking")
load = importlib.import_module("01_load")

if __name__ == "__main__":
    setup_console()

    reset = "--reset" in sys.argv

    client = get_client()
    created = ensure_collection(client)
    print(f"mode={MODE} collection={COLLECTION} "
          f"({'새로 생성' if created else '기존 사용'})")

    if reset and not created:
        # local 모드의 delete_collection 은 Windows 에서 파일 핸들 때문에 실패할 수 있어
        # 컬렉션을 지우지 않고 포인트만 비운다. (vectordb/01_create_collection.py 와 동일)
        client.delete(
            collection_name=COLLECTION,
            points_selector=FilterSelector(filter=Filter()),
            wait=True,
        )
        print("  --reset: 기존 포인트를 모두 비웠습니다.")

    docs = load.load_all()
    chunks = chunking.split_documents(docs)
    print(f"문서 {len(docs)}개 -> 청크 {len(chunks)}개")

    # 문서별로 청크 번호를 0 부터 매겨서 id 를 만든다.
    counter: Counter[str] = Counter()
    ids = []
    for chunk in chunks:
        source = str(chunk.metadata.get("source", "unknown"))
        ids.append(make_point_id(source, counter[source]))
        counter[source] += 1

    store = get_vector_store(client)
    store.add_documents(chunks, ids=ids)

    print(f"색인 완료: {client.count(COLLECTION).count} points")
    print("\n-- 문서별 청크 수 --")
    for source, count in sorted(counter.items()):
        print(f"  {count:>3}개  {Path(source).name}")

    info = client.get_collection(COLLECTION)
    print(f"\nstatus={info.status}")

    # local 모드는 파일 락을 쓰므로 명시적으로 닫아준다.
    client.close()
