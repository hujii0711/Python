"""3단계: 임베딩.

문장을 벡터로 바꾼다. LangChain 의 Embeddings 인터페이스는 메서드가 두 개다.
  - embed_documents(texts) : 색인할 문서 여러 개를 한 번에 (배치 처리)
  - embed_query(text)      : 검색할 질의 하나를

정규화(normalize_embeddings=True)된 벡터라서 내적이 그대로 코사인 유사도가 된다.
아래에서 실제로 유사도를 계산해 의미가 가까운 문장이 실제로 가까운지 확인한다.
"""

import importlib

from _config import EMBED_MODEL, get_device, get_embeddings, setup_console

chunking = importlib.import_module("02_chunking")
load = importlib.import_module("01_load")

SAMPLES = [
    "파이썬에서 리스트를 뒤집는 방법",
    "list reverse in python",
    "판다스로 CSV 파일 읽기",
    "오늘 점심은 김치찌개였다",
]

if __name__ == "__main__":
    setup_console()

    embeddings = get_embeddings()
    print(f"model={EMBED_MODEL} device={get_device()}\n")

    vectors = embeddings.embed_documents(SAMPLES)
    print(f"embed_documents: {len(vectors)}개 x {len(vectors[0])}차원")

    query_vector = embeddings.embed_query(SAMPLES[0])
    print(f"embed_query   : {len(query_vector)}차원")
    norm = sum(v * v for v in query_vector) ** 0.5
    print(f"벡터 크기(L2) : {norm:.4f}  (1.0 이면 정규화된 상태)\n")

    # 정규화된 벡터끼리의 내적 = 코사인 유사도
    print("-- 문장 간 코사인 유사도 --")
    print("      " + "".join(f"{i:>8}" for i in range(len(SAMPLES))))
    for i, a in enumerate(vectors):
        row = "".join(f"{sum(x * y for x, y in zip(a, b)):>8.3f}" for b in vectors)
        print(f"  [{i}] {row}   {SAMPLES[i]}")
    print("\n  0번(한국어)과 1번(영어)이 뜻이 같아서 높게 나오고,")
    print("  3번(일상 문장)은 나머지와 낮게 나오는 것이 정상이다.\n")

    # 실제 색인할 청크를 임베딩하면 시간이 얼마나 걸리는지 감을 잡는다.
    chunks = chunking.split_documents(load.load_all())
    chunk_vectors = embeddings.embed_documents([c.page_content for c in chunks])
    print(f"실제 청크 {len(chunks)}개 임베딩 완료 -> "
          f"{len(chunk_vectors)} x {len(chunk_vectors[0])}")
