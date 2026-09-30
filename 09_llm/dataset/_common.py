"""RAG 데이터셋 실습 공통 헬퍼.

01 ~ 10 스크립트가 공유하는 경로, JSONL 입출력, 해시, 임베딩 로더를 모아둔다.
각 단계는 `build/` 에 JSONL 산출물을 남기고 다음 단계가 그것을 읽는 방식이라,
중간부터 다시 돌리거나 산출물만 따로 들여다보기 쉽다.
"""

import hashlib
import json
import sys
import unicodedata
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable, Iterator

BASE_DIR = Path(__file__).parent
RAW_DIR = BASE_DIR / "raw"      # 코퍼스 원본. 여기 있는 것만 색인 대상이 된다.
EVAL_DIR = BASE_DIR / "eval"    # 평가 자료. 코퍼스에 섞이면 평가가 오염되므로 분리한다.
BUILD_DIR = BASE_DIR / "build"

# 단계별 산출물 파일 이름
CORPUS_RAW = BUILD_DIR / "01_corpus_raw.jsonl"
CORPUS_CLEAN = BUILD_DIR / "02_corpus_clean.jsonl"
CORPUS_DEDUP = BUILD_DIR / "03_corpus_dedup.jsonl"
CHUNKS = BUILD_DIR / "04_chunks.jsonl"
CHUNKS_ENRICHED = BUILD_DIR / "05_chunks_enriched.jsonl"
EVAL_SET = BUILD_DIR / "06_eval_qa.jsonl"
METRICS = BUILD_DIR / "07_retrieval_metrics.json"
TRIPLETS = BUILD_DIR / "08_triplets.jsonl"
SPLITS = BUILD_DIR / "09_chunks_split.jsonl"
DATASET_CARD = BUILD_DIR / "10_dataset_card.md"

EMBED_MODEL = "BAAI/bge-m3"

# --- 플랫폼 분기 ---------------------------------------------------------
IS_WINDOWS = sys.platform == "win32"
IS_MACOS = sys.platform == "darwin"
IS_LINUX = sys.platform.startswith("linux")


def setup_console() -> None:
    """콘솔 인코딩을 한글이 깨지지 않는 상태로 맞춘다.

    macOS / Linux 는 UTF-8 이 기본이라 할 일이 없다. Windows 는 cp949 처럼
    한글을 표현할 수 있는 인코딩이면 그대로 두고, 못 쓰는 인코딩일 때만 UTF-8 로
    바꾼다. 무조건 UTF-8 로 강제하면 cp949 콘솔에서 오히려 깨지기 때문이다.
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
    sep = "\\" if IS_WINDOWS else "/"
    return f"uv run dataset{sep}{script}"


# --- 디바이스 / 임베딩 ---------------------------------------------------
def get_device() -> str:
    """OS 에서 쓸 수 있는 가속기를 고른다.

    - macOS         : Apple Silicon 이면 mps, Intel Mac 이면 cpu (CUDA 없음)
    - Windows/Linux : NVIDIA GPU 가 있으면 cuda, 없으면 cpu (MPS 없음)
    """
    import torch

    if IS_MACOS:
        mps = getattr(torch.backends, "mps", None)
        return "mps" if mps is not None and mps.is_available() else "cpu"
    return "cuda" if torch.cuda.is_available() else "cpu"


@lru_cache(maxsize=1)
def get_embedder():
    """sentence-transformers 모델. 무거우니 한 번만 로드해서 재사용한다."""
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(EMBED_MODEL, device=get_device())


def encode(texts: list[str]):
    """정규화된 임베딩 행렬(numpy). 정규화했으므로 내적 = 코사인 유사도."""
    return get_embedder().encode(
        texts, normalize_embeddings=True, batch_size=32, show_progress_bar=False
    )


# --- JSONL 입출력 --------------------------------------------------------
def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> int:
    """JSONL 로 저장. 줄 단위라 큰 데이터도 스트리밍으로 읽을 수 있다."""
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("w", encoding="utf-8", newline="\n") as f:
        for row in rows:
            # ensure_ascii=False 라야 한글이 \uXXXX 로 부풀지 않는다.
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
            count += 1
    return count


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return list(iter_jsonl(path))


def iter_jsonl(path: Path) -> Iterator[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)


def require(path: Path, produced_by: str) -> Path:
    """이전 단계 산출물이 있는지 확인한다. 없으면 어떤 스크립트를 돌릴지 안내한다."""
    if not path.exists():
        raise SystemExit(
            f"{path.name} 이(가) 없습니다. 먼저 `{run_hint(produced_by)}` 를 실행하세요."
        )
    return path


# --- 텍스트 유틸 ---------------------------------------------------------
def sha256_text(text: str) -> str:
    """내용 기반 식별자. 같은 내용이면 OS 와 실행 시점에 관계없이 같은 값이 나온다."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def stable_bucket(key: str, buckets: int) -> int:
    """문자열을 0 ~ buckets-1 로 고정 배정한다.

    파이썬 내장 hash() 는 실행마다 값이 달라져서(PYTHONHASHSEED) 분할에 쓰면 안 된다.
    sha256 을 쓰면 어느 OS, 어느 실행에서도 같은 결과가 나온다.
    """
    digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
    return int(digest[:8], 16) % buckets


def char_profile(text: str) -> dict[str, float]:
    """글자 종류 비율. 언어 판별과 잡음 탐지에 쓴다."""
    total = len(text) or 1
    hangul = sum(1 for c in text if "가" <= c <= "힣")
    latin = sum(1 for c in text if c.isascii() and c.isalpha())
    digit = sum(1 for c in text if c.isdigit())
    return {
        "hangul_ratio": round(hangul / total, 4),
        "latin_ratio": round(latin / total, 4),
        "digit_ratio": round(digit / total, 4),
    }


def normalize_unicode(text: str) -> str:
    """전각 문자와 호환 문자를 반각 기본형으로 통일한다 (３００ -> 300)."""
    return unicodedata.normalize("NFKC", text)
