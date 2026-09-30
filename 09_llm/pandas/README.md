# RAG 를 위한 pandas 예제 10선

numpy 가 벡터 연산을 맡는다면, pandas 는 **문서/청크 파이프라인과 평가**를 맡습니다.
각 파일은 독립 실행되며 결과가 재현됩니다.

## 실행

```powershell
cd C:\Python\09_llm
uv run pandas\01_load_documents.py
```

전부 한 번에:

```powershell
cd C:\Python\09_llm
Get-ChildItem pandas\[01]*.py | Sort-Object Name | ForEach-Object { "=== $($_.Name) ==="; uv run "pandas\$($_.Name)" }
```

## 목차

RAG 파이프라인 순서대로 배치했습니다.

| 파일 | 단계 | 핵심 내용 |
| --- | --- | --- |
| [01_load_documents.py](01_load_documents.py) | 적재 | CSV/JSONL, dtype 명시, 결측 문서 처리, `json_normalize` |
| [02_clean_text.py](02_clean_text.py) | 정제 | `.str` 체인, 보이지 않는 문자, Copy-on-Write 함정 |
| [03_chunking.py](03_chunking.py) | 청킹 | `explode` 로 1:N 펼치기, `cumcount` 로 chunk_id, 오버랩 |
| [04_metadata_filter.py](04_metadata_filter.py) | 필터 | `query()`, `isin`/`between`, Qdrant Filter 대응표 |
| [05_dedup.py](05_dedup.py) | 중복 제거 | 정확/정규화/해시 중복, 보일러플레이트, 근사 중복 후보 |
| [06_embedding_join.py](06_embedding_join.py) | 임베딩 연결 | **행 순서 어긋남 사고**와 안전한 패턴 |
| [07_eval_metrics.py](07_eval_metrics.py) | 평가 | recall@k / precision@k / MRR / nDCG, A/B 비교 |
| [08_groupby_rerank.py](08_groupby_rerank.py) | 재순위화 | 청크→문서 집계, `transform`, 다양성 라운드로빈 |
| [09_qdrant_roundtrip.py](09_qdrant_roundtrip.py) | 벡터DB 연동 | DataFrame ↔ payload, `scroll` 덤프, **필터 위치 문제** |
| [10_large_corpus.py](10_large_corpus.py) | 대용량 | `chunksize` 스트리밍, parquet, dtype 최적화, 재개 |

09 번은 실제 Qdrant 에 붙습니다. `QDRANT_MODE` 가 그대로 적용되고,
전용 컬렉션 `pandas_demo` 를 쓰고 끝나면 지우므로 기존 데이터를 건드리지 않습니다.

## 실측으로 확인한 것들

숫자는 이 환경(pandas 3.0.6 / Windows / CPU)에서 실제로 측정한 값입니다.

- **`.str` 이 `apply` 보다 느릴 수 있습니다** (02) — 5만건 정규식 정제에서 `.str` 315ms vs `apply` 184ms.
  "벡터화니까 빠르다"는 통념이 정규식에는 통하지 않습니다. `.str` 을 쓰는 진짜 이유는 결측(NA) 자동 처리입니다.
- **parquet 이 CSV 보다 10배 작습니다** (10) — 12.18MB → 1.22MB, 읽기도 2.6배 빠름.
  컬럼만 골라 읽으면 0.330s → 0.023s. dtype 도 보존됩니다.
- **서버 필터와 pandas 필터는 결과가 다릅니다** (09) — 같은 `limit=2` 에서 서버 필터 2건 vs pandas 필터 1건.
  필터는 반드시 `query_filter` 로 서버에서 걸어야 합니다.

## 조용히 망가지는 것들

에러 없이 통과하면서 검색 품질만 떨어뜨리는 것들입니다.

- **임베딩 배열과 DataFrame 행 순서 어긋남** (06) — `sort_values` 나 필터 후 `emb[i]` 를 그대로 쓰면
  전혀 다른 문서의 벡터를 쓰게 됩니다. 에러가 안 나고 "엉뚱한 결과"로만 나타납니다.
  해결: `row_pos` 컬럼을 박아두거나 id 기준 `merge(validate='1:1')`.
- **Chained assignment** (02) — pandas 3.0 은 Copy-on-Write 가 항상 켜져 있어
  `df["col"][0] = 값` 이 조용히 무시됩니다. `.loc[행, 열] = 값` 을 쓰세요.
- **`explode` 의 빈 리스트** (03) — 청크가 0개인 문서가 `NaN` 행을 남깁니다.
- **`and` / `or` 로 조건 결합** (04) — `&` / `|` 와 괄호를 써야 합니다 (`and` 는 `ValueError`).
- **dtype 축소 오버플로** (10) — `int64` 1000 을 `int8` 로 바꾸면 `-24` 가 됩니다. 에러 없음.
- **정제 결과 미대입** (02) — `df["x"].str.strip()` 은 반환값이고 원본을 바꾸지 않습니다.
- **`sum` 으로 문서 점수 집계** (08) — 청크가 많은 문서가 무조건 유리해집니다. 보통 `max` 가 맞습니다.
- **점수 스케일 무시한 하이브리드** — [../numpy/07_hybrid_fusion.py](../numpy/07_hybrid_fusion.py) 참고.

## 이 디렉터리 이름 주의

디렉터리 이름이 `pandas` 라서 패키지 이름과 겹칩니다. **`__init__.py` 를 만들지 마세요.**
만들면 정규 패키지가 되어 site-packages 의 실제 `pandas` 를 가려버립니다.

## 관련 디렉터리

- [../numpy/](../numpy/) — 벡터 연산 쪽 (유사도, top-k, 양자화, MMR)
- [../vectordb/](../vectordb/) — Qdrant 적재와 검색
- [../llm_load/embedding/](../llm_load/embedding/) — 실제 임베딩 모델로 벡터 만들기

역할 분담: **pandas 는 메타데이터, numpy 는 벡터.**
둘을 한 자료구조에 섞지 말고 `row_pos` 나 id 로 명시적으로 연결하세요 (06 예제).
