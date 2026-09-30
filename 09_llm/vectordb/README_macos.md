# macOS 에서 Qdrant 서버 실행하기

`localhost:6333` 에 Qdrant 서버를 띄우는 방법입니다. Windows 쪽 절차는 [README.md](README.md) 를 보세요.

> **검증 범위:** 이 문서는 Windows PC 에서 작성했으므로 macOS 에서 직접 실행해 확인하지는 못했습니다.
> 명령은 공식 릴리스/이미지와 문서를 근거로 했고, 아키텍처·파일 구성 같은 사실은 확인했습니다
> (`qdrant/qdrant:v1.19.1` 의 `linux/arm64` 지원, darwin tarball 내용물 등).
> 대시보드 404 나 실행 위치 의존성처럼 Windows 에서 실제로 겪은 문제는 그대로 표시해 뒀습니다.

## 어떤 방법을 고를까

| 방법 | 추천 | 비고 |
| --- | --- | --- |
| **Docker** | ⭐ 가장 간단 | 대시보드까지 바로 동작. Apple Silicon 네이티브(arm64) |
| **네이티브 바이너리** | Docker 를 못 쓸 때 | 설치 없음. 대시보드는 별도 파일 필요 |
| Homebrew | ❌ 불가 | 서버 formula 가 없음 (아래 참고) |
| 소스 빌드 | ❌ 비추천 | Rust 툴체인 필요, 빌드 오래 걸림 |

---

## 방법 1 — Docker (권장)

### 런타임 설치

셋 중 하나를 고르면 됩니다.

```bash
brew install --cask docker      # Docker Desktop
brew install --cask orbstack    # OrbStack (더 가볍고 빠름)
brew install colima docker      # colima (CLI 전용)
```

`colima` 는 설치 후 VM 을 먼저 띄워야 합니다.

```bash
colima start
```

### 실행

이 저장소의 [docker-compose.yml](docker-compose.yml) 을 그대로 쓸 수 있습니다.

```bash
cd 09_llm/vectordb
docker compose up -d      # 실행
docker compose logs -f    # 로그
docker compose down       # 종료
```

compose 없이 한 줄로 띄우려면:

```bash
docker run -d --name qdrant \
  -p 6333:6333 -p 6334:6334 \
  -v "$(pwd)/qdrant_data:/qdrant/storage" \
  qdrant/qdrant:v1.19.1
```

이미지는 `linux/amd64` + `linux/arm64` 멀티아치이므로 **Apple Silicon 에서 에뮬레이션 없이 네이티브로 돕니다.**
데이터는 `qdrant_data/` 에 남아 컨테이너를 지워도 유지됩니다.

Docker 이미지에는 웹 UI 정적 파일이 포함되어 있어 **대시보드가 바로 동작합니다.**

---

## 방법 2 — 네이티브 바이너리

Docker 없이 실행합니다. 공식 릴리스에 macOS 바이너리가 있습니다.

| 칩 | 파일 |
| --- | --- |
| Apple Silicon (M1~) | `qdrant-aarch64-apple-darwin.tar.gz` |
| Intel | `qdrant-x86_64-apple-darwin.tar.gz` |

tarball 안에는 실행 파일 `qdrant` 하나만 들어 있습니다(약 73MB).

### 설치 스크립트

`09_llm/vectordb/setup_server.sh` 로 저장하고 `chmod +x setup_server.sh` 후 실행하세요.

```bash
#!/usr/bin/env bash
# Qdrant 서버(네이티브 macOS 바이너리) 설치
set -euo pipefail

QDRANT_VERSION="v1.19.1"   # qdrant-client 버전과 맞출 것
WEBUI_VERSION="v0.2.18"

cd "$(dirname "$0")"
SERVER_DIR="$PWD/server"
mkdir -p "$SERVER_DIR"

# 칩에 맞는 타깃 선택
case "$(uname -m)" in
  arm64)  TARGET="aarch64-apple-darwin" ;;
  x86_64) TARGET="x86_64-apple-darwin" ;;
  *) echo "지원하지 않는 아키텍처: $(uname -m)" >&2; exit 1 ;;
esac

# 1) 서버 바이너리
if [[ -x "$SERVER_DIR/qdrant" ]]; then
  echo "qdrant 이미 있음 -> 건너뜀 ($("$SERVER_DIR/qdrant" --version))"
else
  echo "qdrant $QDRANT_VERSION ($TARGET) 내려받는 중..."
  curl -fsSL -o /tmp/qdrant.tar.gz \
    "https://github.com/qdrant/qdrant/releases/download/$QDRANT_VERSION/qdrant-$TARGET.tar.gz"
  tar -xzf /tmp/qdrant.tar.gz -C "$SERVER_DIR"
  rm /tmp/qdrant.tar.gz
  chmod +x "$SERVER_DIR/qdrant"
  # Gatekeeper 격리 속성 제거 (없으면 "개발자를 확인할 수 없습니다" 로 실행 거부됨)
  xattr -d com.apple.quarantine "$SERVER_DIR/qdrant" 2>/dev/null || true
  echo "설치 완료: $("$SERVER_DIR/qdrant" --version)"
fi

# 2) 대시보드 정적 파일 (없으면 /dashboard 가 404)
if [[ -f "$SERVER_DIR/static/index.html" ]]; then
  echo "static/ 이미 있음 -> 건너뜀"
else
  echo "Web UI $WEBUI_VERSION 내려받는 중..."
  curl -fsSL -o /tmp/webui.zip \
    "https://github.com/qdrant/qdrant-web-ui/releases/download/$WEBUI_VERSION/dist-qdrant.zip"
  rm -rf /tmp/qdrant_webui "$SERVER_DIR/static"
  unzip -q /tmp/webui.zip -d /tmp/qdrant_webui
  # 압축 안에 dist/ 로 들어 있으므로 static/ 으로 옮긴다
  mv /tmp/qdrant_webui/dist "$SERVER_DIR/static"
  rm -rf /tmp/webui.zip /tmp/qdrant_webui
  echo "Web UI 설치 완료"
fi

echo
echo "준비 완료. 서버 실행: ./start_server.sh"
```

### 실행 스크립트

`09_llm/vectordb/start_server.sh` 로 저장하고 `chmod +x start_server.sh` 후 실행하세요.

```bash
#!/usr/bin/env bash
# Qdrant 서버를 localhost:6333 에서 실행
set -euo pipefail

cd "$(dirname "$0")"
SERVER_DIR="$PWD/server"

if [[ ! -x "$SERVER_DIR/qdrant" ]]; then
  echo "qdrant 가 없습니다. 먼저 ./setup_server.sh 를 실행하세요." >&2
  exit 1
fi

if lsof -nP -iTCP:6333 -sTCP:LISTEN >/dev/null 2>&1; then
  echo "6333 포트가 이미 사용 중입니다. 기존 서버가 떠 있는지 확인하세요." >&2
  exit 1
fi

echo "REST      : http://localhost:6333"
echo "대시보드  : http://localhost:6333/dashboard"
echo "헬스체크  : http://localhost:6333/healthz"
echo "종료      : Ctrl+C"
echo

# qdrant 는 static/ 과 storage/ 를 현재 디렉터리 기준으로 찾으므로
# 반드시 server 디렉터리에서 실행해야 한다.
cd "$SERVER_DIR"
exec ./qdrant
```

### Gatekeeper 주의

GitHub 에서 받은 바이너리는 공증(notarization)되지 않아 macOS 가 실행을 막습니다.
설치 스크립트가 `xattr -d com.apple.quarantine` 으로 처리하지만, 그래도 막히면:

```bash
xattr -cr server/qdrant
```

그래도 안 되면 **시스템 설정 → 개인정보 보호 및 보안** 에서 "확인 없이 허용" 을 누르세요.

---

## 실행 확인

```bash
curl http://localhost:6333/healthz      # -> healthz check passed
curl http://localhost:6333/collections
open http://localhost:6333/dashboard
```

## 파이썬 스크립트 연결

`QDRANT_MODE=server` 만 주면 됩니다. 다른 터미널에서:

```bash
cd 09_llm
export QDRANT_MODE=server
uv run vectordb/01_create_collection.py
uv run vectordb/02_upsert.py
uv run vectordb/03_search.py
```

FastAPI 서버도 같은 방식입니다.

```bash
cd 09_llm
export QDRANT_MODE=server
uv run fastapi/run.py
```

서버 모드는 여러 프로세스가 동시에 붙을 수 있으므로, FastAPI 를 띄운 채로 위 스크립트를 돌려도 됩니다.

---

## Windows 와 다른 점

- **명령 문법** — `$env:QDRANT_MODE = "server"` → `export QDRANT_MODE=server`,
  경로 구분자 `\` → `/`, `.ps1` → `.sh`.
- **임베딩 장치** — [_client.py](_client.py) 의 `get_device()` 가 Apple Silicon 에서 `mps` 를 고르므로
  `BAAI/bge-m3` 임베딩이 GPU 에서 돕니다. Windows(CPU 전용 torch)보다 빠릅니다.
- **로컬 모드 초기화** — Windows 에서는 파일 핸들이 잡혀 `delete_collection()` 이 디렉터리 삭제에
  실패하고도 `True` 를 반환하는 문제가 있는데, macOS 에서는 정상 동작할 것으로 보입니다.
  단 [01_create_collection.py](01_create_collection.py) 는 양쪽에서 모두 동작하는
  "포인트 비우기" 방식을 쓰므로 그대로 두면 됩니다.
- **Gatekeeper** — Windows 에는 없는 단계입니다 (위 참고).

## Homebrew 로는 안 됩니다

- `homebrew-core` 에 `qdrant` formula 가 없습니다.
- 공식 탭 `qdrant/homebrew-tap` 에는 Qdrant Cloud CLI 캐스크(`qcloud`) 하나뿐이고, **서버는 없습니다.**

`brew install qdrant` 를 시도할 필요 없이 위의 Docker 또는 네이티브 바이너리 방법을 쓰세요.
