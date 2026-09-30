"""어느 디렉터리에서 실행해도 동작하는 서버 실행 스크립트.

    uv run fastapi\\run.py          # 09_llm 에서
    uv run run.py                  # fastapi 에서
    $env:PORT = "9000"; uv run fastapi\\run.py

uvicorn 을 직접 쓰면(`uvicorn main:app`) import string 을 현재 작업 디렉터리 기준으로
해석하기 때문에, 실행 위치가 다르면 엉뚱한 `main.py` 를 잡거나 아예 못 찾는다.
이 스크립트는 자기 위치로 cwd 를 옮긴 뒤 서버를 띄우므로 실행 위치에 영향받지 않는다.
"""

import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
os.chdir(HERE)
# 스크립트로 실행하면 파이썬이 HERE 를 sys.path[0] 에 넣지만,
# 다른 방식으로 불려도 main 을 찾을 수 있게 명시적으로 보장한다.
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import uvicorn

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    # RELOAD=1 은 QDRANT_MODE=memory / server 에서만 쓸 것.
    # 로컬 모드에서는 재시작 시 저장 디렉터리 파일 락이 충돌한다.
    reload = os.getenv("RELOAD") == "1"
    print(f"http://127.0.0.1:{port}/docs")
    uvicorn.run("main:app", host="127.0.0.1", port=port, reload=reload)
