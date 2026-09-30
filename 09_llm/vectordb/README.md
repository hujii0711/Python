# Qdrant 실습 환경

## 구성

| 파일 | 설명 |
| --- | --- |
| `_client.py` | 클라이언트 / 임베딩 모델 공통 헬퍼 |
| `01_create_collection.py` | 컬렉션 생성 + 접속 확인 (있으면 포인트 초기화) |
| `02_upsert.py` | 문서 임베딩 후 저장 |
| `03_search.py` | 유사도 검색 + payload 필터 검색 |
| `setup_server.ps1` | Qdrant 서버 설치 (네이티브 Windows 바이너리) |
| `start_server.ps1` | `localhost:6333` 서버 실행 |
| `docker-compose.yml` | 서버 모드 대안 (Docker 필요) |
| `README_macos.md` | **macOS 에서 서버 실행하는 방법** |

이 문서는 Windows 기준입니다. 맥에서는 [README_macos.md](README_macos.md) 를 보세요.

임베딩 모델은 `BAAI/bge-m3` (1024차원), 거리 함수는 코사인입니다.

## 실행 모드

`QDRANT_MODE` 환경변수로 선택합니다. 기본값은 `local`.

- `local` — **Docker 불필요.** `./qdrant_storage` 디렉터리에 직접 저장. 한 번에 한 프로세스만 접근 가능.
- `memory` — 메모리에만 저장. 프로세스 종료 시 사라짐.
- `server` — `localhost:6333` 의 Qdrant 서버에 접속. 여러 프로세스가 동시에 붙을 수 있음.

## 실행 (로컬 모드, Docker 없이)

```powershell
cd C:\Python\09_llm
uv run vectordb\01_create_collection.py
uv run vectordb\02_upsert.py
uv run vectordb\03_search.py
```

첫 실행 때 bge-m3 모델(약 2.3GB)을 내려받습니다.

## 실행 (서버 모드, localhost:6333)

이 PC 에는 Docker 가 없으므로 **Qdrant 공식 Windows 바이너리**를 씁니다.
WSL / Hyper-V / 관리자 권한 모두 필요 없습니다.

### 1) 최초 1회 설치

```powershell
cd C:\Python\09_llm\vectordb
.\setup_server.ps1
```

`server\qdrant.exe` (85MB) 와 대시보드용 `server\static\` 을 GitHub 공식 릴리스에서 내려받습니다.
이미 있으면 건너뛰므로 여러 번 실행해도 됩니다.

### 2) 서버 실행

```powershell
cd C:\Python\09_llm\vectordb
.\start_server.ps1
```

이 창은 서버가 점유합니다. 종료는 Ctrl+C.

| 주소 | 용도 |
| --- | --- |
| http://localhost:6333 | REST API |
| http://localhost:6333/dashboard | 웹 대시보드 |
| http://localhost:6333/healthz | 헬스체크 |
| `localhost:6334` | gRPC |

### 3) 다른 창에서 스크립트 실행

```powershell
cd C:\Python\09_llm
$env:QDRANT_MODE = "server"
uv run vectordb\01_create_collection.py
uv run vectordb\02_upsert.py
uv run vectordb\03_search.py
```

데이터는 `server\storage\` 에 저장되어 재시작해도 유지됩니다.

### Docker 를 쓰는 경우

Docker Desktop 을 설치했다면 `docker-compose.yml` 로도 같은 서버를 띄울 수 있습니다.

```powershell
cd C:\Python\09_llm\vectordb
docker compose up -d
```

이 PC 의 CPU 가상화는 펌웨어에서 활성화되어 있으므로 Docker Desktop 설치는 가능하지만,
Hyper-V / WSL2 기능 활성화(관리자 권한 + 재부팅)가 필요합니다.

## 참고

- **서버 모드는 여러 프로세스가 동시에 붙을 수 있습니다.** FastAPI 서버를 띄운 채로
  `vectordb` 스크립트를 돌리려면 서버 모드를 쓰세요 (로컬 모드는 파일 락 때문에 불가).
- `qdrant.exe` 는 `static/` 과 `storage/` 를 **현재 디렉터리 기준**으로 찾습니다.
  `start_server.ps1` 이 `server` 디렉터리로 이동한 뒤 실행하는 이유입니다.
  다른 곳에서 실행하면 `/dashboard` 가 404 가 되고 저장소도 딴 곳에 생깁니다.
- 로컬 모드는 저장 디렉터리에 파일 락을 걸기 때문에 **동시에 두 스크립트를 실행할 수 없습니다.**
  `client.close()` 를 빼먹으면 다음 실행에서 락 충돌이 납니다.
- 로컬 모드의 `delete_collection()` 은 Windows 에서 저장 파일 핸들이 열려 있어 디렉터리 삭제에
  실패하는데도 `True` 를 반환합니다. 그래서 `01` 은 컬렉션을 지우는 대신 포인트를 비우는 방식을 씁니다.
  완전히 초기화하려면 `qdrant_storage` 디렉터리를 직접 지우세요.

  ```powershell
  Remove-Item -Recurse -Force C:\Python\09_llm\vectordb\qdrant_storage
  ```
