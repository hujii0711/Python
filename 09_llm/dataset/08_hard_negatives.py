"""예제 8: 하드 네거티브 마이닝 (임베딩 파인튜닝 데이터 만들기).

임베딩 모델을 도메인에 맞게 파인튜닝하려면 (질문, 정답, 오답) 묶음이 필요하다.
이때 오답을 무작위로 고르면 학습이 너무 쉬워서 모델이 배우는 게 없다.
"정답과 헷갈릴 만큼 비슷하지만 정답은 아닌" 것을 골라야 한다. 이게 하드 네거티브다.

고르는 기준
  - 정답이 아니어야 한다 (당연하지만 gold 를 빼는 걸 자주 잊는다)
  - 유사도가 충분히 높아야 한다 (너무 낮으면 easy negative 라 학습에 도움이 안 된다)
  - 유사도가 너무 높으면 안 된다 (사실상 정답인데 라벨만 없는 경우 = false negative)
  - 같은 문서의 다른 청크는 제외할 수 있게 해둔다 (보통 내용이 이어져 위험하다)
"""

import numpy as np

from _common import (
    CHUNKS_ENRICHED,
    EVAL_SET,
    TRIPLETS,
    encode,
    read_jsonl,
    require,
    setup_console,
    write_jsonl,
)

NEGATIVES_PER_QUERY = 3
MIN_SIMILARITY = 0.35   # 이보다 낮으면 너무 쉬운 오답
MAX_SIMILARITY = 0.90   # 이보다 높으면 사실상 정답일 수 있다 (false negative)
EXCLUDE_SAME_DOC = True


def mine(
    query_vectors,
    chunk_vectors,
    chunks: list[dict],
    eval_rows: list[dict],
) -> tuple[list[dict], dict[str, int]]:
    similarity = query_vectors @ chunk_vectors.T
    chunk_ids = [c["chunk_id"] for c in chunks]

    triplets: list[dict] = []
    skipped = {"gold": 0, "same_doc": 0, "too_low": 0, "too_high": 0}

    for row_index, row in enumerate(eval_rows):
        gold = set(row["gold_chunk_ids"])
        gold_docs = {cid.split("::")[0] for cid in gold}

        # 유사도가 높은 순서대로 후보를 훑는다.
        order = np.argsort(-similarity[row_index])
        negatives: list[dict] = []

        for candidate in order:
            if len(negatives) >= NEGATIVES_PER_QUERY:
                break
            chunk = chunks[candidate]
            score = float(similarity[row_index][candidate])

            if chunk_ids[candidate] in gold:
                skipped["gold"] += 1
                continue
            if EXCLUDE_SAME_DOC and chunk["doc_id"] in gold_docs:
                skipped["same_doc"] += 1
                continue
            if score > MAX_SIMILARITY:
                skipped["too_high"] += 1
                continue
            if score < MIN_SIMILARITY:
                skipped["too_low"] += 1
                continue

            negatives.append({"chunk_id": chunk_ids[candidate],
                              "text": chunk["text"],
                              "score": round(score, 4)})

        if not negatives:
            continue

        positive = next(c for c in chunks if c["chunk_id"] in gold)
        triplets.append(
            {
                "qa_id": row["qa_id"],
                "query": row["question"],
                "positive_chunk_id": positive["chunk_id"],
                "positive": positive["text"],
                "negatives": negatives,
                "origin": row["origin"],
            }
        )

    return triplets, skipped


if __name__ == "__main__":
    setup_console()

    require(CHUNKS_ENRICHED, "05_enrich_metadata.py")
    require(EVAL_SET, "06_make_eval_set.py")
    chunks = read_jsonl(CHUNKS_ENRICHED)
    eval_rows = read_jsonl(EVAL_SET)
    print(f"청크 {len(chunks)}개 / 질문 {len(eval_rows)}건\n")

    print("임베딩 중...")
    chunk_vectors = encode([c["text"] for c in chunks])
    query_vectors = encode([r["question"] for r in eval_rows])

    triplets, skipped = mine(query_vectors, chunk_vectors, chunks, eval_rows)
    written = write_jsonl(TRIPLETS, triplets)

    print(f"\n트리플렛 {written}건 -> {TRIPLETS.name}")
    total_negatives = sum(len(t["negatives"]) for t in triplets)
    print(f"오답 총 {total_negatives}개 "
          f"(질문당 평균 {total_negatives / max(len(triplets), 1):.1f}개)")

    print("\n-- 후보에서 걸러낸 이유 --")
    labels = {
        "gold": "정답이라서",
        "same_doc": "정답과 같은 문서라서",
        "too_high": f"유사도가 {MAX_SIMILARITY} 초과라 사실상 정답일 수 있어서",
        "too_low": f"유사도가 {MIN_SIMILARITY} 미만이라 너무 쉬워서",
    }
    for key, count in skipped.items():
        print(f"  {labels[key]:<45} {count}회")

    print("\n-- 예시 --")
    for triplet in triplets[:2]:
        print(f"  [질문] {triplet['query']}")
        print(f"    정답 {triplet['positive_chunk_id']}: "
              f"{triplet['positive'][:50].replace(chr(10), ' ')}...")
        for negative in triplet["negatives"]:
            print(f"    오답 {negative['score']:.3f} {negative['chunk_id']}: "
                  f"{negative['text'][:45].replace(chr(10), ' ')}...")
        print()

    print("이 파일은 sentence-transformers 의 MultipleNegativesRankingLoss 나")
    print("TripletLoss 학습 입력으로 바로 쓸 수 있는 모양이다.")
    print("주의: 임계값을 잘못 잡으면 정답과 다를 게 없는 청크를 오답으로 학습시켜")
    print("모델을 오히려 망가뜨린다. 처음에는 샘플을 눈으로 확인하는 편이 안전하다.")
