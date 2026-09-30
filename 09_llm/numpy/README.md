# RAG 를 위한 numpy 예제 10선

RAG 시스템을 만들 때 실제로 쓰게 되는 numpy 연산들. 각 파일은 독립 실행되며,
`np.random.default_rng(0)` 으로 결과가 재현됩니다.

## 실행

```powershell
cd C:\Python\09_llm
uv run numpy\01_embedding_array.py
```

전부 한 번에 돌려보려면:

```powershell
cd C:\Python\09_llm
Get-ChildItem numpy\*.py | Sort-Object Name | ForEach-Object { "=== $($_.Name) ==="; uv run "numpy\$($_.Name)" }
```

## 목차

| 파일 | 주제 | 핵심 내용 |
| --- | --- | --- |
| [01_embedding_array.py](01_embedding_array.py) | 임베딩 배열 기본 | shape / dtype / 메모리, float32 를 쓰는 이유, L2 정규화 |
| [02_similarity.py](02_similarity.py) | 유사도 3종 | 코사인 = 정규화 후 내적, 유클리드와 순위가 같은 이유, 1:N / M:N |
| [03_topk.py](03_topk.py) | Top-K 추출 | `argpartition` 이 `argsort` 보다 빠른 이유와 함정 |
| [04_batch_search.py](04_batch_search.py) | 배치 검색 | 점수 행렬 메모리 추정, 청크 분할 검색 (결과 동일 검증) |
| [05_normalize_pitfalls.py](05_normalize_pitfalls.py) | 정규화 함정 6가지 | axis / keepdims / 영벡터 nan / in-place 오염 / dtype 승격 |
| [06_mmr.py](06_mmr.py) | MMR 다양성 재순위화 | 중복 청크로 컨텍스트 낭비하는 문제를 순수 numpy 로 해결 |
| [07_hybrid_fusion.py](07_hybrid_fusion.py) | 하이브리드 점수 결합 | RRF / min-max / z-score, 그냥 더하면 안 되는 이유 |
| [08_quantization.py](08_quantization.py) | 벡터 양자화 | int8 / binary, 재현율 측정, 후보 추리기 + 재채점 패턴 |
| [09_pooling.py](09_pooling.py) | 풀링 | 마스크 없는 mean pooling 버그, 청크 → 문서 집계 |
| [10_persist_memmap.py](10_persist_memmap.py) | 저장과 memmap | `.npy` / `.npz`, RAM 에 안 올리고 검색, Windows 파일 잠금 |

## 특히 조용히 망가지는 것들

에러 없이 통과하면서 검색 품질만 떨어뜨리는 것들입니다. 각 파일에서 실측으로 보여줍니다.

- **마스크 없는 mean pooling** (09) — 패딩까지 평균에 넣으면 짧은 문장의 임베딩이 0 쪽으로 끌려갑니다.
- **`int8 @ int8`** (08) — numpy 는 int32 로 자동 승격하지 **않습니다.** 오버플로로 값이 완전히 달라지는데 에러는 안 납니다.
- **영벡터 정규화** (05) — 빈 청크가 `nan` 을 만들고, `nan` 하나가 이후 점수 전체와 `argmax` 를 오염시킵니다.
- **`axis` / `keepdims` 누락** (05) — `axis` 를 빼면 에러 없이 전부 틀린 값이 나옵니다.
- **정규화 안 한 내적** (02) — 벡터가 '긴' 문서가 부당하게 유리해집니다.
- **점수를 그냥 더하는 하이브리드** (07) — BM25 스케일이 커서 벡터 검색 결과가 무시됩니다.

## 이 디렉터리 이름 주의

디렉터리 이름이 `numpy` 라서 패키지 이름과 겹칩니다. **`__init__.py` 를 만들지 마세요.**
만들면 정규 패키지가 되어 site-packages 의 실제 `numpy` 를 가려버립니다.
(`__init__.py` 가 없으면 namespace 패키지로만 인식되어 실제 `numpy` 가 이깁니다.)

## 관련 디렉터리

- [../vectordb/](../vectordb/) — 여기 개념들이 Qdrant 에서 어떻게 제공되는지
- [../llm_load/embedding/](../llm_load/embedding/) — 실제 임베딩 모델(`BAAI/bge-m3`)로 벡터 만들기

numpy 파일 저장은 임베딩 캐시나 오프라인 평가용입니다.
필터링 / 증분 갱신 / 동시 접근이 필요하면 벡터DB 를 쓰세요 (10번 예제 마지막 참고).
