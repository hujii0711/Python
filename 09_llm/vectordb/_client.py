"""Qdrant 클라이언트/임베딩 모델 공통 헬퍼.

MODE 환경변수로 접속 방식을 고른다.
  - local  (기본) : 별도 서버 없이 ./qdrant_storage 디렉터리에 저장
  - memory        : 프로세스 메모리에만 저장 (테스트용)
  - server        : docker compose 로 띄운 Qdrant 서버에 접속
"""

import os
from functools import lru_cache
from pathlib import Path

import torch
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

MODE = os.getenv("QDRANT_MODE", "local")
HOST = os.getenv("QDRANT_HOST", "localhost")
PORT = int(os.getenv("QDRANT_PORT", "6333"))

STORAGE_PATH = Path(__file__).parent / "qdrant_storage"
COLLECTION = "docs"
MODEL_NAME = "BAAI/bge-m3"
VECTOR_SIZE = 1024  # bge-m3 dense 차원


def get_client() -> QdrantClient:
    if MODE == "memory":
        return QdrantClient(location=":memory:")
    if MODE == "server":
        return QdrantClient(host=HOST, port=PORT)
    if MODE == "local":
        return QdrantClient(path=str(STORAGE_PATH))
    raise ValueError(f"알 수 없는 QDRANT_MODE: {MODE}")


def get_device() -> str:
    if torch.cuda.is_available():
        return "cuda"
    if torch.backends.mps.is_available():
        return "mps"
    return "cpu"


@lru_cache(maxsize=1)
def get_model() -> SentenceTransformer:
    return SentenceTransformer(MODEL_NAME, device=get_device())


def encode(texts: list[str]):
    return get_model().encode(texts, normalize_embeddings=True, batch_size=32)
