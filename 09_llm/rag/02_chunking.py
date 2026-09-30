"""2단계: 청킹(분할).

임베딩 모델은 한 번에 넣을 수 있는 길이가 정해져 있고, 검색 단위가 너무 크면
질문과 상관없는 내용까지 함께 딸려온다. 그래서 문서를 적당한 크기로 자른다.

세 가지 방식을 같은 문서에 적용해서 결과를 비교한다.
  - RecursiveCharacterTextSplitter : 문단 → 줄 → 문장 → 글자 순으로 쪼갠다 (기본 선택)
  - MarkdownHeaderTextSplitter     : 제목 구조를 살려서 쪼개고 제목을 메타데이터로 남긴다
  - SentenceTransformersTokenTextSplitter : 임베딩 모델 토크나이저 기준으로 쪼갠다
"""

import importlib

from _config import CHUNK_OVERLAP, CHUNK_SIZE, EMBED_MODEL, setup_console
from langchain_core.documents import Document
from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
    SentenceTransformersTokenTextSplitter,
)

load = importlib.import_module("01_load")


def get_recursive_splitter() -> RecursiveCharacterTextSplitter:
    """색인 단계에서도 쓰는 기본 분할기.

    separators 를 문단 → 줄 → 문장부호 → 공백 순으로 두면
    되도록 의미 단위가 끊기지 않는 지점에서 잘린다.
    """
    return RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", "다. ", " ", ""],
        length_function=len,
        add_start_index=True,  # metadata["start_index"] 로 원문 위치가 남는다
    )


def split_documents(docs: list[Document]) -> list[Document]:
    """다른 스크립트에서 재사용하는 진입점."""
    return get_recursive_splitter().split_documents(docs)


def show(label: str, chunks: list[Document], limit: int = 3) -> None:
    lengths = [len(c.page_content) for c in chunks]
    print(f"-- {label} --")
    print(f"  청크 {len(chunks)}개 / 길이 최소 {min(lengths)}, 최대 {max(lengths)}, "
          f"평균 {sum(lengths) // len(lengths)}")
    for chunk in chunks[:limit]:
        preview = chunk.page_content[:70].replace("\n", " ")
        print(f"  [{len(chunk.page_content):>4}자] {preview}...")
        print(f"         metadata={chunk.metadata}")
    if len(chunks) > limit:
        print(f"  ... 이하 {len(chunks) - limit}개 생략")
    print()


if __name__ == "__main__":
    setup_console()

    docs = load.load_all()
    print(f"원본 문서 {len(docs)}개\n")

    show("RecursiveCharacterTextSplitter (전체 문서)", split_documents(docs))

    # 마크다운은 제목 구조가 이미 의미 단위이므로 헤더로 먼저 나누는 편이 낫다.
    md_docs = [d for d in docs if str(d.metadata.get("source", "")).endswith(".md")]
    header_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=[("#", "title"), ("##", "section")],
        strip_headers=False,
    )
    md_chunks: list[Document] = []
    for doc in md_docs:
        for chunk in header_splitter.split_text(doc.page_content):
            # split_text 는 원본 metadata 를 모르므로 source 를 직접 옮겨준다.
            chunk.metadata = {**doc.metadata, **chunk.metadata}
            md_chunks.append(chunk)
    show(f"MarkdownHeaderTextSplitter (.md {len(md_docs)}개)", md_chunks)

    # 글자 수가 아니라 실제 토큰 수로 잘라야 모델 입력 한계를 정확히 맞출 수 있다.
    token_splitter = SentenceTransformersTokenTextSplitter(
        model_name=EMBED_MODEL, tokens_per_chunk=128, chunk_overlap=16
    )
    show("SentenceTransformersTokenTextSplitter (128 토큰)",
         token_splitter.split_documents(docs))
