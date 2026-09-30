# LangChain RAG 실습

문서 로드 → 청킹 → 임베딩 → 색인 → 검색 → 답변 생성까지 한 단계씩 나눠서 실행해 본다.
벡터 저장소는 [../vectordb](../vectordb) 와 같은 Qdrant 를 쓰지만 컬렉션과 저장 디렉터리는 따로 둔다.

## 구성

| 파일              | 단계   | 설명                                                    |
| ----------------- | ------ | ------------------------------------------------------- |
| `_config.py`      | -      | 임베딩 / 벡터스토어 / 경로 공통 설정                    |
| `01_load.py`      | 로드   | `.md` `.txt` `.csv` `.pdf` → `Document` 리스트          |
| `02_chunking.py`  | 청킹   | 분할기 3종 비교 (글자 기준 / 마크다운 헤더 / 토큰 기준) |
| `03_embedding.py` | 임베딩 | `embed_documents` / `embed_query`, 코사인 유사도 확인   |
| `04_index.py`     | 색인   | 청크를 Qdrant 컬렉션에 저장 (재실행해도 중복 없음)      |
| `05_search.py`    | 검색   | 유사도 / 점수 / MMR / 메타데이터 필터 / Retriever       |
| `06_rag_chain.py` | 생성   | 검색 결과를 프롬프트에 넣어 로컬 LLM 으로 답변          |
| `docs/`           | -      | 실습용 샘플 문서 (파이썬·판다스·Qdrant 메모, FAQ CSV)   |

| 설정             | 값                               | 바꾸는 방법                                   |
| ---------------- | -------------------------------- | --------------------------------------------- |
| 임베딩 모델      | `BAAI/bge-m3` (1024차원, 코사인) | `_config.py` 의 `EMBED_MODEL`                 |
| 컬렉션           | `rag_docs`                       | `_config.py` 의 `COLLECTION`                  |
| 청크 크기 / 겹침 | 500자 / 80자                     | `_config.py` 의 `CHUNK_SIZE`, `CHUNK_OVERLAP` |
| 답변 생성 모델   | `Qwen/Qwen2.5-0.5B-Instruct`     | `RAG_LLM` 환경변수                            |
| Qdrant 접속      | `local`                          | `QDRANT_MODE` 환경변수                        |

## 실행

```powershell
cd C:\Python\09_llm
uv sync

uv run rag\01_load.py       # 문서가 어떻게 읽히는지
uv run rag\02_chunking.py   # 분할 방식별 결과 비교
uv run rag\03_embedding.py  # 벡터 차원 / 유사도 확인
uv run rag\04_index.py      # 색인 (필수)
uv run rag\05_search.py     # 검색
uv run rag\06_rag_chain.py  # 질문 → 답변
```

`04_index.py` 를 먼저 실행해야 `05_search.py` 와 `06_rag_chain.py` 가 동작한다.
`04_index.py --reset` 은 기존 포인트를 모두 비우고 처음부터 색인한다.

첫 실행 때 bge-m3(약 2.3GB)와 답변 생성 모델을 내려받는다.

### macOS

명령의 경로 구분자만 바뀐다.

```bash
cd ~/Python/09_llm   # 저장소를 받은 위치
uv sync

uv run rag/00_env_check.py
uv run rag/01_load.py
uv run rag/04_index.py
uv run rag/06_rag_chain.py
```

`local` 모드는 Docker 없이 바로 돌아간다. 서버 모드가 필요하면
[../vectordb/README_macos.md](../vectordb/README_macos.md) 를 보면 된다.

**Apple Silicon(arm64) 전용이다.** `uv.lock` 의 torch 2.14 는 macOS 휠이
`macosx_14_0_arm64` 하나뿐이라 Intel Mac 에서는 `uv sync` 단계에서 실패한다.
Intel Mac 이면 torch 버전을 낮춰 다시 잠가야 한다. macOS 14 (Sonoma) 이상이 필요하다.

## OS 분기

OS 에 따라 달라지는 부분은 `_config.py` 한 곳에 모아 두고, 나머지 스크립트는 그것을 가져다 쓴다.

| 헬퍼 | Windows | macOS |
| --- | --- | --- |
| `IS_WINDOWS` / `IS_MACOS` / `IS_LINUX` | `sys.platform` 으로 판별한 상수 | 〃 |
| `get_device()` | `cuda` 있으면 cuda, 없으면 cpu | Apple Silicon 이면 `mps`, Intel Mac 이면 cpu |
| `get_torch_dtype()` | cpu → float32 / cuda → float16 | cpu → float32 / mps → float16 |
| `setup_console()` | 콘솔이 한글을 못 쓰는 인코딩일 때만 UTF-8 로 교정 | 아무것도 하지 않음 (UTF-8 이 기본) |
| `run_hint("04_index.py")` | `uv run rag\04_index.py` | `uv run rag/04_index.py` |

macOS 에는 CUDA 가 없고 Windows 에는 MPS 가 없으므로 `get_device()` 는 OS 를 먼저 보고 갈린다.

`setup_console()` 은 **무조건 UTF-8 로 바꾸지 않는다.** cp949 콘솔은 한글을 정상적으로
출력하는데 거기서 UTF-8 로 강제하면 오히려 깨지기 때문에, 현재 인코딩으로 한글을 쓸 수
없을 때만 교정한다.

파일 경로는 분기하지 않고 `pathlib` 로 처리한다. `Path(...).name` 같은 API 가 두 OS 에서
같은 결과를 주므로 직접 `\` 나 `/` 를 다루는 것보다 안전하다.

## 실행 모드

`QDRANT_MODE` 환경변수로 선택한다. 기본값은 `local`.

- `local` — `rag/qdrant_storage` 디렉터리에 직접 저장. 파일 락 때문에 한 번에 한 프로세스만 붙을 수 있다.
- `memory` — 메모리에만 저장. 프로세스 종료 시 사라진다.
- `server` — `localhost:6333` 의 Qdrant 서버에 접속. 여러 프로세스가 동시에 붙을 수 있다.

서버를 띄우는 방법은 [../vectordb/README.md](../vectordb/README.md) 를 보면 된다.

```powershell
$env:QDRANT_MODE = "server"
uv run rag\04_index.py
```

## 알아두면 좋은 점

**중복 색인** — 포인트 id 를 `uuid5(문서 경로 + 청크 번호)` 로 고정했다.
같은 문서를 다시 색인하면 같은 id 에 덮어써지므로 `04_index.py` 를 여러 번 돌려도 포인트 수가 늘지 않는다.
Qdrant 포인트 id 는 부호 없는 정수나 UUID 만 허용하기 때문에 경로 문자열을 그대로 쓸 수는 없다.

**메타데이터 필터** — LangChain 은 `Document.metadata` 를 payload 의 `metadata` 키 아래에 넣는다.
그래서 필터 키가 `source` 가 아니라 `metadata.source` 다.

**청크 크기** — 크면 문맥이 풍부하지만 관련 없는 내용이 섞이고, 작으면 정확하지만 문맥이 끊긴다.
`02_chunking.py` 로 같은 문서가 방식별로 몇 개 청크가 되는지 보면서 조절한다.
마크다운처럼 제목 구조가 있는 문서는 `MarkdownHeaderTextSplitter` 로 먼저 나누는 편이 결과가 낫다.

**로컬 모드 락** — 스크립트 끝에서 `client.close()` 를 호출한다.
안 닫으면 다음 스크립트가 같은 디렉터리에 붙지 못한다.

**답변 품질** — 기본 모델(0.5B)은 CPU 에서 돌아가는 크기라 검색은 정확해도 요약이 어설플 수 있다.
검색 단계가 제대로 되는지는 `05_search.py` 로 따로 확인하고, 답변 품질은 더 큰 모델로 올린다.

```powershell
$env:RAG_LLM = "Qwen/Qwen2.5-1.5B-Instruct"
uv run rag\06_rag_chain.py
```

**PDF** — `docs/` 에 PDF 를 넣으면 `PyPDFLoader` 가 페이지 단위로 읽는다 (없으면 건너뛴다).

**langchain-community 경고** — `TextLoader` / `CSVLoader` / `PyPDFLoader` 는 `langchain_community` 에 있고
이 패키지는 sunset 예고 상태라 import 할 때 DeprecationWarning 이 뜬다. 동작에는 문제가 없다.

---

09_llm/rag/에 LangChain 기반 RAG 파이프라인을 단계별 스크립트로 만들었습니다. 6개 스크립트 전부 실제로 실행해서 exit 0을 확인했습니다.

파일 단계 내용
\_config.py 공통 임베딩·벡터스토어·경로 팩토리, QDRANT_MODE 처리 (vectordb/\_client.py와 같은 규칙)
01_load.py 로드 DirectoryLoader+TextLoader(md/txt), CSVLoader, PyPDFLoader → 8 documents
02_chunking.py 청킹 RecursiveCharacterTextSplitter(11청크) / MarkdownHeaderTextSplitter(8) / SentenceTransformersTokenTextSplitter(16) 비교
03_embedding.py 임베딩 HuggingFaceEmbeddings(bge-m3, 1024차원), 코사인 유사도 행렬로 검증
04_index.py 색인 QdrantVectorStore.add_documents, --reset 지원
05_search.py 검색 유사도 / 점수 / MMR / 메타데이터 필터 / as_retriever / 임계값 필터
06_rag_chain.py 생성 LCEL 체인 retriever → format_docs → prompt → ChatHuggingFace → parser
샘플 문서 4개(docs/: 파이썬·판다스·Qdrant 메모 + FAQ CSV)와 README.md도 함께 넣었습니다.

구현하면서 실제로 걸렸던 부분들:

포인트 id — uuid5(문서경로 + 청크번호)로 고정했습니다. 04_index.py를 3번 돌려도 11 points 유지(확인함). Qdrant는 id에 정수/UUID만 허용해서 경로 문자열을 그대로 쓸 수 없습니다.
필터 키 — LangChain이 metadata를 payload의 metadata 하위에 넣어서, 필터 키가 metadata.source입니다.
벡터 이름 — QdrantVectorStore가 이름 없는(빈 문자열) dense 벡터를 기대하므로 컬렉션 생성 시 vectors_config={"": VectorParams(...)}로 맞췄습니다.
LLM device — HuggingFacePipeline.from_model_id는 device를 CUDA 인덱스 정수로만 받고 device_map은 accelerate를 요구합니다(실제로 에러 발생). transformers 파이프라인을 직접 만들어 HuggingFacePipeline(pipeline=...)으로 감싸는 방식으로 바꿨습니다 — cuda/mps/cpu 모두 커버됩니다.
두 가지 알아두실 점:

pyproject.toml에 langchain, langchain-community, langchain-huggingface, langchain-qdrant, pypdf를 추가하고 uv sync했습니다. LangChain 1.4.3이 설치됐고, langchain-community는 sunset 예고 상태라 import 시 DeprecationWarning이 뜹니다(동작은 정상). 로더 대체 패키지가 아직 없어서 그대로 썼습니다.
이 PC는 CUDA/MPS가 없어 CPU로 돌았고, 기본 생성 모델은 캐시에 있던 Qwen2.5-0.5B-Instruct로 잡았습니다. 검색은 정확했지만(예: "리스트 뒤집기" → python_basics.md 0.61점 1위) 0.5B 모델이라 요약이 어설픕니다 — 한 질문에서는 "원본 보존"을 물었는데 reverse()라고 답했습니다. $env:RAG_LLM로 더 큰 모델을 지정하도록 해뒀고 README에도 적었습니다.
