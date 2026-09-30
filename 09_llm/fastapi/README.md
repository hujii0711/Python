# FastAPI 웹서버 (Qdrant 연동)

## 구성

| 파일 | 역할 |
| --- | --- |
| `main.py` | FastAPI 앱 — 헬스체크 + Qdrant 연동 테스트 |
| `run.py` | 실행 위치에 영향받지 않는 서버 실행 스크립트 (권장) |
| `smoke_test.py` | 서버를 띄우지 않고 전체 엔드포인트를 호출하는 스모크 테스트 |

Qdrant 접속 설정(모드 / 컬렉션 / 임베딩 모델)은 `../vectordb/_client.py` 를 그대로 재사용합니다.
따라서 `QDRANT_MODE` 환경변수(`local` 기본 / `memory` / `server`)가 여기에도 그대로 적용됩니다.

**서버 모드를 권장합니다.** 로컬 모드는 파일 락 때문에 이 서버가 떠 있는 동안
`vectordb` 스크립트를 실행할 수 없습니다. 서버 모드는 동시 접속이 됩니다.

```powershell
# 창 1: Qdrant 서버 (최초 1회는 .\setup_server.ps1 먼저)
cd C:\Python\09_llm\vectordb; .\start_server.ps1

# 창 2: FastAPI
cd C:\Python\09_llm; $env:QDRANT_MODE = "server"; uv run fastapi\run.py
```

## 엔드포인트

| 메서드 | 경로 | 설명 |
| --- | --- | --- |
| GET | `/` | 서버 정보 (모드, 컬렉션, 모델) |
| GET | `/health` | 웹서버 헬스체크. 외부 의존성을 타지 않음 |
| GET | `/health/qdrant` | Qdrant 접속 + 컬렉션 상태. 접속 실패 시 503 |
| GET | `/health/embedding` | 임베딩 모델 로드 + 차원 검증. 첫 호출은 느림 |
| POST | `/search` | 질의 임베딩 → Qdrant 검색 (엔드투엔드 연동 테스트) |
| GET | `/docs` | Swagger UI |

## 실행

Qdrant 데이터가 먼저 있어야 합니다.

```powershell
cd C:\Python\09_llm
uv run vectordb\01_create_collection.py
uv run vectordb\02_upsert.py
```

서버 실행 — `run.py` 를 쓰면 실행 위치를 신경 쓸 필요가 없습니다.

```powershell
cd C:\Python\09_llm
uv run fastapi\run.py
```

포트 변경은 `PORT` 환경변수로 합니다. 기본 8000.

```powershell
$env:PORT = "9000"; uv run fastapi\run.py
```

http://localhost:8000/docs 에서 바로 호출해볼 수 있습니다.

### uvicorn 을 직접 쓰는 경우

uvicorn 은 `main:app` 을 **현재 작업 디렉터리** 기준으로 찾기 때문에,
반드시 이 디렉터리 안에서 실행해야 합니다.

```powershell
cd C:\Python\09_llm\fastapi
uv run uvicorn main:app --port 8000
```

위치가 틀리면 아래처럼 에러 메시지가 갈립니다.

| 실행 위치 | 에러 |
| --- | --- |
| `09_llm\vectordb` 등 `main.py` 가 없는 곳 | `Error loading ASGI app. Could not import module "main".` |
| `09_llm` | `Attribute "app" not found in module "main".` — `09_llm\main.py` 를 잡음 |
| `C:\Python` (uv 프로젝트 밖) | `Failed to spawn: uvicorn / program not found` |

### 호출 예시

```powershell
curl http://localhost:8000/health
curl http://localhost:8000/health/qdrant
```

한글 질의는 셸이 인라인 인자의 UTF-8 을 깨뜨리는 경우가 많습니다
(`{"detail":"There was an error parsing the body"}` 가 뜨면 이 문제입니다).
**http://localhost:8000/docs 의 Swagger UI 나 `smoke_test.py` 를 쓰는 게 가장 편하고**,
curl 로 보내려면 UTF-8 파일로 저장해서 `--data-binary` 로 넘기세요.

```powershell
'{"query": "판다스로 CSV 파일 읽는 방법", "limit": 2}' | Out-File -Encoding utf8 q.json
curl -X POST http://localhost:8000/search -H "Content-Type: application/json" --data-binary "@q.json"
```

### 스모크 테스트

서버를 띄우지 않고 한 번에 전부 확인:

```powershell
cd C:\Python\09_llm\fastapi
uv run smoke_test.py
```

## 주의사항

- **이 디렉터리에 `__init__.py` 를 만들지 마세요.** 디렉터리 이름이 `fastapi` 라서,
  `__init__.py` 가 있으면 정규 패키지가 되어 site-packages 의 실제 `fastapi` 패키지를 가려버립니다.
  (`__init__.py` 가 없으면 namespace 패키지로만 인식되어 정규 패키지인 실제 `fastapi` 가 이깁니다.)
  같은 이유로 uvicorn 은 `09_llm` 이 아니라 **이 디렉터리 안에서** `main:app` 으로 실행합니다.
- **로컬 모드에서는 서버가 떠 있는 동안 `vectordb` 스크립트를 실행할 수 없습니다.**
  로컬 모드는 저장 디렉터리에 파일 락을 걸고, 앱이 lifespan 동안 클라이언트를 붙잡고 있기 때문입니다.
  같은 이유로 로컬 모드에서는 `--reload` 를 쓰지 마세요 (재시작 시 락이 충돌합니다).
  개발 중 자동 리로드가 필요하면 `QDRANT_MODE` 를 `memory` 또는 `server` 로 두고
  `RELOAD=1 uv run fastapi\run.py` 로 실행하세요.
- 임베딩과 Qdrant 클라이언트는 모두 동기(blocking) 코드라서, 해당 엔드포인트는 `async def` 가 아닌
  `def` 로 정의했습니다. FastAPI 가 threadpool 에서 실행하므로 이벤트 루프를 막지 않습니다.
