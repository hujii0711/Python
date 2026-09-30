"""0단계: 실행 환경 점검.

Windows / macOS 중 어디서 돌든 이 스크립트가 통과하면 나머지 단계도 돌아간다.
어떤 디바이스를 쓰게 되는지, Qdrant 접속 설정이 무엇인지, 모델이 이미 받아져
있는지를 한 번에 보여준다.
"""

import platform
import sys

from _config import (
    COLLECTION,
    DOCS_DIR,
    EMBED_MODEL,
    IS_LINUX,
    IS_MACOS,
    IS_WINDOWS,
    LLM_MODEL,
    MODE,
    STORAGE_PATH,
    get_device,
    get_torch_dtype,
    run_hint,
    setup_console,
)

if __name__ == "__main__":
    setup_console()

    import torch

    os_name = "Windows" if IS_WINDOWS else "macOS" if IS_MACOS else (
        "Linux" if IS_LINUX else sys.platform
    )
    print("-- 실행 환경 --")
    print(f"  OS         : {os_name} ({platform.platform()})")
    print(f"  CPU 아키텍처: {platform.machine()}")
    print(f"  Python     : {sys.version.split()[0]}")
    print(f"  torch      : {torch.__version__}")
    print(f"  콘솔 인코딩 : {sys.stdout.encoding}")

    print("\n-- 디바이스 --")
    device = get_device()
    print(f"  선택된 디바이스 : {device} (dtype={get_torch_dtype()})")
    if IS_MACOS:
        mps = getattr(torch.backends, "mps", None)
        available = mps is not None and mps.is_available()
        print(f"  mps 사용 가능   : {available}"
              f"{'' if available else '  (Intel Mac 이면 cpu 로 동작)'}")
    else:
        print(f"  cuda 사용 가능  : {torch.cuda.is_available()}")

    print("\n-- 데이터 / 저장소 --")
    print(f"  문서 디렉터리 : {DOCS_DIR}")
    sources = sorted(p.name for p in DOCS_DIR.glob("*") if p.is_file())
    print(f"  문서 파일     : {len(sources)}개 {sources}")
    print(f"  QDRANT_MODE   : {MODE}")
    print(f"  컬렉션        : {COLLECTION}")
    if MODE == "local":
        exists = STORAGE_PATH.exists()
        print(f"  저장 경로     : {STORAGE_PATH} ({'있음' if exists else '아직 없음'})")

    print("\n-- 모델 --")
    print(f"  임베딩 : {EMBED_MODEL}")
    print(f"  생성   : {LLM_MODEL}")
    print("  (처음 실행하면 내려받느라 시간이 걸린다)")

    print(f"\n다음 단계: {run_hint('01_load.py')}")
