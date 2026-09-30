"""FastAPI 웹서버 — 헬스체크 + Qdrant 연동 테스트.

실행 (이 디렉터리에서):
    uv run uvicorn main:app --port 8000

주의: 이 디렉터리에는 `__init__.py` 를 만들지 말 것.
      만들면 정규 패키지가 되어 site-packages 의 실제 `fastapi` 패키지를 가려버린다.
"""

import sys
from contextlib import asynccontextmanager
from pathlib import Path

# vectordb/_client.py 의 설정(접속 모드 / 컬렉션 / 임베딩 모델)을 그대로 재사용한다.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "vectordb"))

from _client import (
    COLLECTION,
    MODE,
    MODEL_NAME,
    VECTOR_SIZE,
    encode,
    get_client,
    get_device,
)
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from qdrant_client.models import FieldCondition, Filter, MatchValue

state: dict = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 로컬 모드는 저장 디렉터리에 파일 락을 걸기 때문에, 이 서버가 떠 있는 동안에는
    # vectordb 의 스크립트를 실행할 수 없다. (서버 모드에서는 해당 없음)
    state["client"] = get_client()
    yield
    state["client"].close()
    state.clear()


app = FastAPI(
    title="Qdrant 연동 테스트 API",
    description="웹서버 헬스체크와 Qdrant 연동 상태를 확인하는 실습용 API",
    version="0.1.0",
    lifespan=lifespan,
)


class SearchRequest(BaseModel):
    query: str = Field(min_length=1, examples=["리스트 순서를 거꾸로 만들고 싶어요"])
    limit: int = Field(default=3, ge=1, le=20)
    category: str | None = Field(default=None, examples=["python"])


class SearchHit(BaseModel):
    id: int | str
    score: float
    text: str | None
    category: str | None


@app.get("/", summary="서버 정보")
async def root() -> dict:
    return {
        "service": "Qdrant 연동 테스트 API",
        "qdrant_mode": MODE,
        "collection": COLLECTION,
        "embedding_model": MODEL_NAME,
        "docs": "/docs",
    }


@app.get("/health", summary="웹서버 헬스체크")
async def health() -> dict:
    """웹서버 자체가 살아있는지만 확인한다. 외부 의존성을 타지 않는다."""
    return {"status": "ok"}


@app.get("/health/qdrant", summary="Qdrant 연동 헬스체크")
def health_qdrant() -> dict:
    """Qdrant 에 실제로 접속해서 컬렉션 상태를 확인한다.

    접속 자체가 실패하면 503, 접속은 되지만 컬렉션이 없으면 정상 응답에
    `collection_exists: false` 로 알려준다 (01_create_collection.py 를 먼저 실행해야 함).
    """
    client = state["client"]
    try:
        collections = [c.name for c in client.get_collections().collections]
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Qdrant 접속 실패 (mode={MODE}): {exc}",
        ) from exc

    result = {
        "status": "ok",
        "mode": MODE,
        "collections": collections,
        "collection": COLLECTION,
        "collection_exists": COLLECTION in collections,
    }
    if result["collection_exists"]:
        info = client.get_collection(COLLECTION)
        result |= {
            "collection_status": str(info.status),
            "points": client.count(COLLECTION).count,
            "vector_size": info.config.params.vectors.size,
            "distance": str(info.config.params.vectors.distance),
        }
    else:
        result["hint"] = (
            "vectordb/01_create_collection.py 와 02_upsert.py 를 먼저 실행하세요."
        )
    return result


@app.get("/health/embedding", summary="임베딩 모델 헬스체크")
def health_embedding() -> dict:
    """임베딩 모델을 로드해서 차원이 컬렉션 설정과 맞는지 확인한다.

    첫 호출은 모델 로딩 때문에 수십 초 걸릴 수 있다.
    """
    try:
        vector = encode(["헬스체크"])[0]
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"임베딩 실패: {exc}") from exc

    dim = len(vector)
    return {
        "status": "ok" if dim == VECTOR_SIZE else "mismatch",
        "model": MODEL_NAME,
        "device": get_device(),
        "dim": dim,
        "expected_dim": VECTOR_SIZE,
    }


@app.post("/search", response_model=list[SearchHit], summary="벡터 검색")
def search(request: SearchRequest) -> list[SearchHit]:
    """질의를 임베딩해서 Qdrant 에서 유사 문서를 찾는다 (엔드투엔드 연동 테스트)."""
    client = state["client"]
    if not client.collection_exists(COLLECTION):
        raise HTTPException(
            status_code=503,
            detail=f"'{COLLECTION}' 컬렉션이 없습니다. vectordb/01_create_collection.py 를 먼저 실행하세요.",
        )

    query_filter = None
    if request.category:
        query_filter = Filter(
            must=[
                FieldCondition(key="category", match=MatchValue(value=request.category))
            ]
        )

    points = client.query_points(
        collection_name=COLLECTION,
        query=encode([request.query])[0].tolist(),
        query_filter=query_filter,
        limit=request.limit,
        with_payload=True,
    ).points

    return [
        SearchHit(
            id=point.id,
            score=point.score,
            text=(point.payload or {}).get("text"),
            category=(point.payload or {}).get("category"),
        )
        for point in points
    ]
