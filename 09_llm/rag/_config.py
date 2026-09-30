"""LangChain RAG 실습 공통 설정.

임베딩 모델 / 벡터스토어 / LLM 을 만드는 팩토리를 모아둔다.
vectordb/_client.py 와 같은 규칙으로 QDRANT_MODE 환경변수를 따른다.
  - local  (기본) : rag/qdrant_storage 디렉터리에 직접 저장
  - memory        : 프로세스 메모리에만 저장 (테스트용)
  - server        : docker / qdrant.exe 로 띄운 서버에 접속
"""

import os
import sys
import uuid
from functools import lru_cache
from pathlib import Path

import torch
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

BASE_DIR = Path(__file__).parent
DOCS_DIR = BASE_DIR / "docs"
STORAGE_PATH = BASE_DIR / "qdrant_storage"

# --- 플랫폼 분기 ---------------------------------------------------------
IS_WINDOWS = sys.platform == "win32"
IS_MACOS = sys.platform == "darwin"
IS_LINUX = sys.platform.startswith("linux")


def setup_console() -> None:
    """콘솔 인코딩을 한글이 깨지지 않는 상태로 맞춘다.

    macOS / Linux 는 UTF-8 이 기본이라 할 일이 없다.
    Windows 만 코드페이지가 UTF-8 이 아닐 수 있는데, cp949 처럼 한글을 표현할 수
    있는 인코딩이면 그대로 둔다. 무조건 UTF-8 로 바꾸면 cp949 콘솔에서 오히려
    깨지기 때문에, 한글을 못 쓰는 인코딩일 때만 UTF-8 로 되돌린다.
    """
    if not IS_WINDOWS:
        return
    for stream in (sys.stdout, sys.stderr):
        encoding = getattr(stream, "encoding", None) or ""
        try:
            "한글".encode(encoding)
        except (LookupError, UnicodeEncodeError):
            stream.reconfigure(encoding="utf-8", errors="replace")


def run_hint(script: str) -> str:
    """안내 메시지에 쓸 OS 별 실행 명령. 경로 구분자가 다르다."""
    return f"uv run rag\\{script}" if IS_WINDOWS else f"uv run rag/{script}"


# --- Qdrant --------------------------------------------------------------
MODE = os.getenv("QDRANT_MODE", "local")
HOST = os.getenv("QDRANT_HOST", "localhost")
PORT = int(os.getenv("QDRANT_PORT", "6333"))

COLLECTION = "rag_docs"

EMBED_MODEL = "BAAI/bge-m3"
VECTOR_SIZE = 1024  # bge-m3 dense 차원
# QdrantVectorStore 는 이름 없는(빈 문자열) dense 벡터를 기본으로 쓴다.
VECTOR_NAME = QdrantVectorStore.VECTOR_NAME

# 답변 생성 모델. 더 큰 모델을 쓰려면 RAG_LLM 환경변수로 바꾼다.
LLM_MODEL = os.getenv("RAG_LLM", "mlx-community/Qwen2.5-7B-Instruct-4bit")

# 청킹 기본값. 한국어 문단 기준으로 이 정도가 무난하다.
CHUNK_SIZE = 500
CHUNK_OVERLAP = 80


def get_device() -> str:
    """OS 에서 쓸 수 있는 가속기를 고른다.

    - macOS         : Apple Silicon 이면 mps, Intel Mac 이면 cpu (macOS 에 CUDA 는 없다)
    - Windows/Linux : NVIDIA GPU 가 있으면 cuda, 없으면 cpu (여기에 mps 는 없다)
    """
    if IS_MACOS:
        mps = getattr(torch.backends, "mps", None)
        if mps is not None and mps.is_available():
            return "mps"
        return "cpu"

    if torch.cuda.is_available():
        return "cuda"
    return "cpu"


def get_torch_dtype():
    """디바이스별 모델 가중치 dtype.

    cpu 에서 float16 은 느리거나 아예 지원되지 않는 연산이 있어서 float32 를 쓴다.
    cuda / mps 는 float16 으로 올려야 메모리와 속도 모두 유리하다.
    """
    return torch.float32 if get_device() == "cpu" else torch.float16


@lru_cache(maxsize=1)
def get_embeddings() -> HuggingFaceEmbeddings:
    """LangChain 임베딩 래퍼. 내부적으로 sentence-transformers 를 쓴다."""
    return HuggingFaceEmbeddings(
        model_name=EMBED_MODEL,
        model_kwargs={"device": get_device()},
        encode_kwargs={"normalize_embeddings": True, "batch_size": 32},
    )


def get_client() -> QdrantClient:
    if MODE == "memory":
        return QdrantClient(location=":memory:")
    if MODE == "server":
        return QdrantClient(host=HOST, port=PORT)
    if MODE == "local":
        return QdrantClient(path=str(STORAGE_PATH))
    raise ValueError(f"알 수 없는 QDRANT_MODE: {MODE}")


def ensure_collection(client: QdrantClient) -> bool:
    """컬렉션이 없으면 만든다. 새로 만들었으면 True."""
    if client.collection_exists(COLLECTION):
        return False
    client.create_collection(
        collection_name=COLLECTION,
        vectors_config={
            VECTOR_NAME: VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE)
        },
    )
    return True


def get_vector_store(client: QdrantClient | None = None) -> QdrantVectorStore:
    """색인과 검색에 함께 쓰는 벡터스토어."""
    client = client or get_client()
    ensure_collection(client)
    return QdrantVectorStore(
        client=client,
        collection_name=COLLECTION,
        embedding=get_embeddings(),
    )


def make_point_id(source: str, chunk_index: int) -> str:
    """문서 경로 + 청크 번호로 고정된 UUID 를 만든다.

    id 가 고정되면 같은 문서를 다시 색인해도 덮어쓰기가 되어 중복이 쌓이지 않는다.
    Qdrant 포인트 id 는 부호 없는 정수나 UUID 만 허용한다.
    """
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"{source}#{chunk_index}"))


def format_docs(docs) -> str:
    """검색된 문서를 프롬프트에 넣을 하나의 문자열로 합친다."""
    return "\n\n".join(
        f"[{i}] (출처: {Path(d.metadata.get('source', '?')).name})\n{d.page_content}"
        for i, d in enumerate(docs, start=1)
    )
