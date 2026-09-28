네, 가능합니다. 컨테이너 안에 Ollama를 설치하지 않고, **호스트(맥)에서 실행 중인 Ollama에 컨테이너가 네트워크로 접속**하면 됩니다. 이미 받아 둔 모델도 그대로 쓸 수 있습니다.

## 맥에서 특히 중요한 점

Docker Desktop for Mac은 리눅스 VM 안에서 컨테이너를 돌리기 때문에 **컨테이너에서 Apple GPU(Metal)를 쓸 수 없습니다.** 그래서 컨테이너 안에 Ollama를 띄우면 CPU로만 돌아 매우 느립니다.

| 방식 | GPU 가속 | 추천 |
|---|---|---|
| 호스트 Ollama + 컨테이너에서 API 호출 | Metal 사용 | 강력 추천 |
| 컨테이너 안에 Ollama 설치 | CPU만 | 비추천 |

앞에서 말씀드린 MLX-LM도 같은 이유로 컨테이너 안에서는 쓸 수 없습니다. 호스트에서 돌리고 API로 호출하는 구조가 맞습니다.

## 1단계: 호스트에서 Ollama 실행

```bash
ollama serve          # 앱으로 설치했다면 이미 실행 중
ollama list           # 호스트에 받아 둔 모델 확인
curl http://localhost:11434/api/tags   # 호스트에서 응답 확인
```

Ollama는 기본적으로 `127.0.0.1:11434`에만 열립니다. Docker Desktop의 `host.docker.internal`은 보통 이 주소로도 연결되지만, 접속이 거부되면 아래처럼 바인딩을 넓혀야 합니다.

```bash
# 터미널에서 직접 실행할 때
OLLAMA_HOST=0.0.0.0:11434 ollama serve

# 맥 앱(GUI)으로 설치한 경우
launchctl setenv OLLAMA_HOST "0.0.0.0:11434"
# 이후 Ollama 앱을 종료했다가 다시 실행
```

`0.0.0.0`으로 열면 같은 네트워크의 다른 기기도 접속할 수 있습니다. Ollama에는 인증이 없으니 공용 Wi-Fi에서는 방화벽을 확인하거나, 꼭 필요할 때만 여세요.

## 2단계: 컨테이너에서 호스트 Ollama 호출

Docker Desktop(맥, Windows)에서는 컨테이너 안에서 `host.docker.internal`이 호스트를 가리킵니다.

```bash
docker run --rm curlimages/curl \
  http://host.docker.internal:11434/api/tags
```

### 파이썬 (ollama 라이브러리)

```python
from ollama import Client

client = Client(host="http://host.docker.internal:11434")

res = client.chat(
    model="llama3.2",
    messages=[{"role": "user", "content": "안녕하세요"}],
)
print(res["message"]["content"])
```

### 파이썬 (OpenAI 호환 API)

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://host.docker.internal:11434/v1",
    api_key="ollama",   # 아무 값이나 가능
)
res = client.chat.completions.create(
    model="llama3.2",
    messages=[{"role": "user", "content": "안녕하세요"}],
)
print(res.choices[0].message.content)
```

## docker-compose 예제

호스트 주소를 환경변수로 빼 두면 코드를 바꾸지 않고 설정만 조정할 수 있습니다.

```yaml
services:
  app:
    build: .
    environment:
      OLLAMA_HOST: http://host.docker.internal:11434
    # 리눅스 호스트에서도 host.docker.internal을 쓰려면 아래 추가
    extra_hosts:
      - "host.docker.internal:host-gateway"
```

```python
import os
from ollama import Client

client = Client(host=os.environ.get("OLLAMA_HOST", "http://localhost:11434"))
```

`ollama` 라이브러리는 `OLLAMA_HOST` 환경변수를 자동으로 읽기 때문에 `Client()`만 써도 동작합니다.

## 안 될 때 확인할 것

- **`Connection refused`**: 호스트 Ollama가 `127.0.0.1`에만 열려 있는 경우입니다. 위의 `OLLAMA_HOST=0.0.0.0:11434` 설정을 적용하고 재시작하세요.
- **`host.docker.internal`을 찾지 못함**: Docker Desktop이 아닌 환경(리눅스 Docker Engine 등)에서는 `extra_hosts`로 `host-gateway`를 추가해야 합니다.
- **`localhost`로 접속하면 안 됨**: 컨테이너 안의 `localhost`는 컨테이너 자신입니다. 호스트가 아닙니다.
- **모델이 없다는 오류**: 호스트에서 `ollama list`로 이름을 확인하고, 태그(`llama3.2:3b` 등)까지 정확히 맞춰야 합니다.
- **첫 응답이 느림**: 모델이 메모리에 로드되는 시간입니다. 이후에는 빨라지고, 기본적으로 5분간 유휴 상태면 메모리에서 내려갑니다. 유지하려면 요청에 `keep_alive`를 지정하세요.

```python
client.chat(model="llama3.2", messages=[...], keep_alive="30m")
```

## 정리

호스트 Ollama를 쓰면 컨테이너는 가볍게 유지하면서 Metal 가속과 이미 받은 모델을 그대로 활용할 수 있습니다. 컨테이너에는 애플리케이션 코드만 넣고, 모델 실행은 호스트에 맡기는 구조를 추천합니다.