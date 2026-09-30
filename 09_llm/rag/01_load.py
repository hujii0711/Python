"""1단계: 문서 로드.

LangChain 의 Document Loader 로 여러 형식의 파일을 Document 리스트로 읽는다.
Document 는 본문 `page_content` 와 메타데이터 `metadata` 두 부분으로 되어 있고,
이후 모든 단계(청킹 → 임베딩 → 색인 → 검색)가 이 구조를 그대로 넘겨받는다.
"""

from _config import DOCS_DIR, setup_console
from langchain_community.document_loaders import (
    CSVLoader,
    DirectoryLoader,
    PyPDFLoader,
    TextLoader,
)
from langchain_core.documents import Document


def load_text_files() -> list[Document]:
    """.md / .txt 를 디렉터리 단위로 읽는다.

    DirectoryLoader 는 glob 으로 파일을 고르고 loader_cls 로 각 파일을 읽는다.
    한글 파일은 encoding 을 명시해야 Windows 기본 코드페이지로 읽다가 깨지지 않는다.
    """
    docs: list[Document] = []
    for pattern in ("**/*.md", "**/*.txt"):
        loader = DirectoryLoader(
            str(DOCS_DIR),
            glob=pattern,
            loader_cls=TextLoader,
            loader_kwargs={"encoding": "utf-8"},
        )
        docs.extend(loader.load())
    return docs


def load_csv_files() -> list[Document]:
    """CSV 는 한 행이 한 Document 가 된다.

    source_column 을 주면 그 열의 값이 metadata["source"] 로 들어간다.
    여기서는 행 번호가 남도록 기본 동작(파일 경로 + row)을 그대로 쓴다.
    """
    docs: list[Document] = []
    for path in sorted(DOCS_DIR.glob("*.csv")):
        loader = CSVLoader(str(path), encoding="utf-8")
        docs.extend(loader.load())
    return docs


def load_pdf_files() -> list[Document]:
    """PDF 는 한 페이지가 한 Document 가 된다 (metadata["page"] 로 구분).

    docs/ 에 PDF 를 넣어두면 자동으로 읽는다. 없으면 건너뛴다.
    """
    docs: list[Document] = []
    for path in sorted(DOCS_DIR.glob("*.pdf")):
        docs.extend(PyPDFLoader(str(path)).load())
    return docs


def load_all() -> list[Document]:
    """다른 스크립트에서 재사용하는 진입점."""
    return load_text_files() + load_csv_files() + load_pdf_files()


if __name__ == "__main__":
    setup_console()

    groups = {
        "텍스트(.md/.txt)": load_text_files(),
        "CSV(.csv)": load_csv_files(),
        "PDF(.pdf)": load_pdf_files(),
    }

    for label, docs in groups.items():
        print(f"-- {label}: {len(docs)} documents --")
        for doc in docs:
            preview = doc.page_content[:60].replace("\n", " ")
            print(f"  {len(doc.page_content):>5}자  {preview}...")
            print(f"         metadata={doc.metadata}")
        print()

    total = sum(len(docs) for docs in groups.values())
    chars = sum(len(d.page_content) for docs in groups.values() for d in docs)
    print(f"합계: {total} documents / {chars}자")
