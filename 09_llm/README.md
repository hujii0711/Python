GET /health 웹서버 헬스체크 — 외부 의존성 없음
GET /health/qdrant Qdrant 접속 + 컬렉션 상태, 실패 시 503
GET /health/embedding 임베딩 모델 로드 + 차원 검증
POST /search 질의 임베딩 → Qdrant 검색 (엔드투엔드)
GET /docs Swagger UI
