"""예제 9: train / valid / test 분할.

분할에서 가장 흔한 실수는 같은 문서에서 나온 청크가 train 과 test 에 나뉘어 들어가는
것이다. 내용이 거의 같으니 test 점수가 실제보다 높게 나온다(데이터 누수).

그래서 두 가지를 지킨다.
  1) 문서 단위로 묶어서 분할한다 (그룹 분할). 한 문서의 청크는 전부 같은 쪽으로 간다.
  2) 카테고리 비율을 최대한 맞춘다 (층화). 한쪽에만 몰리면 평가가 편향된다.

무작위 추출에 random.shuffle 을 쓰지 않고 sha256 기반 고정 배정을 쓴다.
파이썬 내장 hash() 는 실행마다 값이 달라지고, seed 를 고정해도 파이썬 버전이 바뀌면
결과가 달라질 수 있다. 해시 배정은 어느 OS, 어느 실행에서도 같은 분할을 준다.
"""

from collections import defaultdict

import pandas as pd

from _common import (
    CHUNKS_ENRICHED,
    SPLITS,
    read_jsonl,
    require,
    setup_console,
    stable_bucket,
    write_jsonl,
)

# 비율 (train, valid, test). 100 개 버킷으로 나눠 배정한다.
RATIOS = {"train": 70, "valid": 15, "test": 15}
BUCKETS = 100


def assign_split(doc_id: str) -> str:
    """문서 하나를 어느 split 으로 보낼지 정한다. 같은 doc_id 는 항상 같은 결과."""
    bucket = stable_bucket(doc_id, BUCKETS)
    edge = 0
    for name, ratio in RATIOS.items():
        edge += ratio
        if bucket < edge:
            return name
    return "train"


def round_robin(docs_by_category: dict[str, list[str]]) -> list[str]:
    """카테고리를 번갈아 가며 문서를 한 줄로 세운다.

    카테고리별로 따로 비율을 적용하면 안 된다. 문서가 2~3개뿐인 카테고리에서
    15%를 반올림하면 0이 되어 valid 가 통째로 비어버린다.
    대신 라운드로빈으로 섞어 한 줄로 세운 뒤 전체를 비율대로 자르면,
    전체 비율은 정확히 맞으면서 카테고리도 자연히 흩어진다.
    """
    # 카테고리 안에서는 해시 순으로 세운다. 순서가 고정되면서도 골고루 섞인다.
    queues = {
        category: sorted(doc_ids, key=lambda d: stable_bucket(d, BUCKETS * 100))
        for category, doc_ids in docs_by_category.items()
    }
    ordered: list[str] = []
    depth = 0
    while len(ordered) < sum(len(q) for q in queues.values()):
        for category in sorted(queues):  # 카테고리 이름 순 = 실행마다 같은 순서
            if depth < len(queues[category]):
                ordered.append(queues[category][depth])
        depth += 1
    return ordered


def stratified_assign(docs_by_category: dict[str, list[str]]) -> dict[str, str]:
    """라운드로빈으로 세운 줄을 전체 비율대로 자른다."""
    ordered = round_robin(docs_by_category)
    total = len(ordered)

    train_end = round(total * RATIOS["train"] / 100)
    valid_end = train_end + round(total * RATIOS["valid"] / 100)
    # 문서가 아주 적어도 valid / test 가 비지 않도록 최소 1개는 확보한다.
    if total >= 3:
        train_end = min(train_end, total - 2)
        valid_end = max(valid_end, train_end + 1)
        valid_end = min(valid_end, total - 1)

    assignment: dict[str, str] = {}
    for index, doc_id in enumerate(ordered):
        if index < train_end:
            assignment[doc_id] = "train"
        elif index < valid_end:
            assignment[doc_id] = "valid"
        else:
            assignment[doc_id] = "test"
    return assignment


if __name__ == "__main__":
    setup_console()

    require(CHUNKS_ENRICHED, "05_enrich_metadata.py")
    chunks = read_jsonl(CHUNKS_ENRICHED)
    print(f"입력: {len(chunks)}개 청크 ({CHUNKS_ENRICHED.name})\n")

    docs_by_category: dict[str, list[str]] = defaultdict(list)
    seen: set[str] = set()
    for chunk in chunks:
        if chunk["doc_id"] not in seen:
            seen.add(chunk["doc_id"])
            docs_by_category[chunk["category"]].append(chunk["doc_id"])

    print(f"문서 {len(seen)}개 / 카테고리 {len(docs_by_category)}종")

    # 두 방식을 비교해 보여준다.
    plain = {doc_id: assign_split(doc_id) for doc_id in seen}
    stratified = stratified_assign(docs_by_category)

    for chunk in chunks:
        chunk["split"] = stratified[chunk["doc_id"]]

    written = write_jsonl(SPLITS, chunks)
    print(f"분할 결과 {written}개 청크 -> {SPLITS.name}\n")

    frame = pd.DataFrame(chunks)

    print("-- split 별 크기 --")
    for name in RATIOS:
        subset = frame[frame["split"] == name]
        docs = subset["doc_id"].nunique()
        print(f"  {name:<6} 문서 {docs:>2}개 / 청크 {len(subset):>2}개 "
              f"({len(subset) / len(frame) * 100:>4.1f}%)")

    print("\n-- 카테고리 x split (층화가 됐는지 확인) --")
    pivot = pd.crosstab(frame["category"], frame["split"])
    for name in RATIOS:
        if name not in pivot.columns:
            pivot[name] = 0
    print(pivot[list(RATIOS)].to_string())

    print("\n-- 누수 검사: 한 문서가 여러 split 에 걸쳐 있는가 --")
    leaked = frame.groupby("doc_id")["split"].nunique()
    leaked = leaked[leaked > 1]
    print(f"  {len(leaked)}개 (0 이어야 정상)")

    print("\n-- 단순 해시 배정과 비교 --")
    plain_counts: dict[str, int] = {}
    for name in plain.values():
        plain_counts[name] = plain_counts.get(name, 0) + 1
    strat_counts: dict[str, int] = {}
    for name in stratified.values():
        strat_counts[name] = strat_counts.get(name, 0) + 1
    print(f"  단순 해시 : {plain_counts}")
    print(f"  층화      : {strat_counts}")
    print("  문서 수가 적으면 단순 해시는 비율이 크게 흔들린다. 층화 쪽이 안정적이다.")
