"""서버를 띄우지 않고 모든 엔드포인트를 한 번씩 호출해보는 스모크 테스트.

실행 (이 디렉터리에서):
    uv run smoke_test.py
"""

import json

from fastapi.testclient import TestClient

from main import app


def show(label: str, response) -> None:
    print(f"\n[{response.status_code}] {label}")
    print(json.dumps(response.json(), ensure_ascii=False, indent=2))


with TestClient(app) as client:
    show("GET /", client.get("/"))
    show("GET /health", client.get("/health"))
    show("GET /health/qdrant", client.get("/health/qdrant"))
    show("GET /health/embedding", client.get("/health/embedding"))
    show(
        "POST /search",
        client.post("/search", json={"query": "리스트 순서를 거꾸로 만들고 싶어요", "limit": 3}),
    )
    show(
        "POST /search (category=pandas)",
        client.post(
            "/search",
            json={"query": "리스트 순서를 거꾸로 만들고 싶어요", "limit": 3, "category": "pandas"},
        ),
    )
