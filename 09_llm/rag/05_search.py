"""5단계: 검색.

색인된 컬렉션에서 질의와 가까운 청크를 찾는다. 네 가지 방식을 비교한다.
  - similarity_search             : 가장 기본. 유사도 top k
  - similarity_search_with_score  : 점수까지 함께 (임계값으로 걸러낼 때 필요)
  - max_marginal_relevance_search : 비슷한 청크가 몰리지 않게 다양성을 섞음(MMR)
  - as_retriever                  : 체인에 끼울 수 있는 Retriever 객체

먼저 04_index.py 를 실행해 두어야 한다.
"""

from pathlib import Path

from _config import (
    COLLECTION,
    DOCS_DIR,
    get_client,
    get_vector_store,
    run_hint,
    setup_console,
)
from qdrant_client.models import FieldCondition, Filter, MatchValue

QUERY = "리스트 순서를 거꾸로 만들고 싶어요"


def show(docs, scores=None) -> None:
    for i, doc in enumerate(docs):
        source = Path(doc.metadata.get("source", "?")).name
        preview = doc.page_content[:64].replace("\n", " ")
        prefix = f"  {scores[i]:.4f}" if scores else "  -     "
        print(f"{prefix}  [{source}] {preview}...")
    print()


if __name__ == "__main__":
    setup_console()

    client = get_client()
    if not client.collection_exists(COLLECTION):
        raise SystemExit(
            f"컬렉션이 없습니다. 먼저 `{run_hint('04_index.py')}` 를 실행하세요."
        )

    store = get_vector_store(client)
    print(f"저장된 청크: {client.count(COLLECTION).count} points")
    print(f"[query] {QUERY}\n")

    print("-- 1) similarity_search (top 3) --")
    show(store.similarity_search(QUERY, k=3))

    print("-- 2) similarity_search_with_score (top 3) --")
    hits = store.similarity_search_with_score(QUERY, k=3)
    show([doc for doc, _ in hits], [score for _, score in hits])

    print("-- 3) MMR (fetch_k=8 에서 다양성 고려해 3개, lambda_mult=0.5) --")
    show(store.max_marginal_relevance_search(QUERY, k=3, fetch_k=8, lambda_mult=0.5))

    print("-- 4) 메타데이터 필터: faq.csv 안에서만 검색 --")
    # payload 는 metadata_payload_key("metadata") 아래에 들어가므로 키가 metadata.source 다.
    faq_filter = Filter(
        must=[
            FieldCondition(
                key="metadata.source",
                match=MatchValue(value=str(DOCS_DIR / "faq.csv")),
            )
        ]
    )
    hits = store.similarity_search_with_score(
        "청크 크기는 어떻게 정하나요?", k=2, filter=faq_filter
    )
    show([doc for doc, _ in hits], [score for _, score in hits])

    print("-- 5) Retriever 인터페이스 (체인에 그대로 끼울 수 있다) --")
    retriever = store.as_retriever(search_kwargs={"k": 3})
    show(retriever.invoke("판다스에서 결측치를 채우는 방법"))

    print("-- 6) 점수 임계값 필터 (0.5 미만은 관련 없다고 판단) --")
    for doc, score in store.similarity_search_with_score("우주선 연료 계산법", k=3):
        verdict = "채택" if score >= 0.5 else "버림"
        preview = doc.page_content[:40].replace("\n", " ")
        print(f"  {score:.4f}  {verdict}  {preview}...")

    client.close()
