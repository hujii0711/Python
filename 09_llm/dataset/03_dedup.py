"""예제 3: 중복 / 근사 중복 제거.

같은 내용이 여러 번 색인되면 검색 결과 상위가 같은 문서로 채워져서 실제로 볼 수 있는
정보가 줄어든다. 백업 파일, 복사본, 조금만 고친 개정판이 대표적인 원인이다.

두 가지를 단계적으로 쓴다.
  1) 정확 중복 : sha256 해시가 같은 문서. 빠르고 확실하다. 먼저 이걸로 걸러낸다.
  2) 근사 중복 : 몇 글자만 다른 문서. 두 가지 방법을 비교한다.
       - 문자 n-gram 자카드 : 모델이 필요 없고 빠르다. 표현이 다르면 못 잡는다.
       - 임베딩 코사인      : 표현이 달라도 의미가 같으면 잡는다. 대신 느리다.

어느 쪽을 남길지도 정해야 한다. 여기서는 본문이 더 긴 쪽을 대표로 남긴다.
"""

from itertools import combinations

from _common import (
    CORPUS_CLEAN,
    CORPUS_DEDUP,
    encode,
    read_jsonl,
    require,
    setup_console,
    write_jsonl,
)

SHINGLE_SIZE = 5       # 문자 n-gram 길이
JACCARD_THRESHOLD = 0.7
COSINE_THRESHOLD = 0.95  # 임베딩은 웬만하면 높게 잡아야 오탐이 적다


def shingles(text: str, size: int = SHINGLE_SIZE) -> set[str]:
    """문자 단위 n-gram 집합.

    한국어는 띄어쓰기가 불규칙해서 단어 단위보다 문자 단위가 안정적이다.
    """
    compact = "".join(text.split())
    if len(compact) < size:
        return {compact}
    return {compact[i : i + size] for i in range(len(compact) - size + 1)}


def jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def find_exact_duplicates(records: list[dict]) -> dict[str, list[str]]:
    """sha256 -> doc_id 목록. 2건 이상이면 정확 중복이다."""
    groups: dict[str, list[str]] = {}
    for record in records:
        groups.setdefault(record["sha256"], []).append(record["doc_id"])
    return {h: ids for h, ids in groups.items() if len(ids) > 1}


if __name__ == "__main__":
    setup_console()

    require(CORPUS_CLEAN, "02_clean_text.py")
    records = read_jsonl(CORPUS_CLEAN)
    print(f"입력: {len(records)}건 ({CORPUS_CLEAN.name})\n")

    # --- 1) 정확 중복 -----------------------------------------------------
    exact_groups = find_exact_duplicates(records)
    print(f"-- 정확 중복(sha256) {len(exact_groups)}개 그룹 --")
    drop_ids: set[str] = set()
    for digest, doc_ids in exact_groups.items():
        by_id = {r["doc_id"]: r for r in records}
        # 본문이 긴 쪽을 대표로, 길이가 같으면 이름이 짧은 쪽(대개 원본)을 남긴다.
        keep = min(doc_ids, key=lambda i: (-by_id[i]["char_len"], len(i), i))
        losers = [i for i in doc_ids if i != keep]
        drop_ids.update(losers)
        print(f"  {digest[:12]}... : {doc_ids} -> {keep} 유지")
    if not exact_groups:
        print("  없음")

    survivors = [r for r in records if r["doc_id"] not in drop_ids]

    # --- 2) 근사 중복: 문자 n-gram 자카드 ---------------------------------
    print(f"\n-- 근사 중복 A: 문자 {SHINGLE_SIZE}-gram 자카드 >= {JACCARD_THRESHOLD} --")
    shingle_map = {r["doc_id"]: shingles(r["text"]) for r in survivors}
    jaccard_pairs = []
    for a, b in combinations(survivors, 2):
        score = jaccard(shingle_map[a["doc_id"]], shingle_map[b["doc_id"]])
        if score >= JACCARD_THRESHOLD:
            jaccard_pairs.append((score, a, b))
    for score, a, b in sorted(jaccard_pairs, reverse=True, key=lambda t: t[0]):
        print(f"  {score:.3f}  {a['doc_id']} <-> {b['doc_id']}")
    if not jaccard_pairs:
        print("  없음")

    # --- 3) 근사 중복: 임베딩 코사인 --------------------------------------
    print(f"\n-- 근사 중복 B: 임베딩 코사인 >= {COSINE_THRESHOLD} --")
    print("  (bge-m3 로 임베딩 중...)")
    vectors = encode([r["text"] for r in survivors])
    similarity = vectors @ vectors.T  # 정규화된 벡터라 내적 = 코사인

    cosine_pairs = []
    for i, j in combinations(range(len(survivors)), 2):
        score = float(similarity[i][j])
        if score >= COSINE_THRESHOLD:
            cosine_pairs.append((score, survivors[i], survivors[j]))
    for score, a, b in sorted(cosine_pairs, reverse=True, key=lambda t: t[0]):
        print(f"  {score:.3f}  {a['doc_id']} <-> {b['doc_id']}")
    if not cosine_pairs:
        print("  없음")

    # --- 4) 근사 중복 제거: 긴 쪽을 대표로 남긴다 --------------------------
    near_drop: set[str] = set()
    for _, a, b in jaccard_pairs + cosine_pairs:
        if a["doc_id"] in near_drop or b["doc_id"] in near_drop:
            continue
        # 같은 기준으로 대표를 고르고 나머지를 버린다.
        rank = lambda r: (-r["char_len"], len(r["doc_id"]), r["doc_id"])
        loser = b if rank(a) < rank(b) else a
        near_drop.add(loser["doc_id"])

    final = [r for r in survivors if r["doc_id"] not in near_drop]
    written = write_jsonl(CORPUS_DEDUP, final)

    print("\n-- 결과 --")
    print(f"  입력          {len(records)}건")
    print(f"  정확 중복 제거 -{len(drop_ids)}건 {sorted(drop_ids)}")
    print(f"  근사 중복 제거 -{len(near_drop)}건 {sorted(near_drop)}")
    print(f"  최종          {written}건 -> {CORPUS_DEDUP.name}")

    print("\n두 방법 비교: 자카드는 글자가 겹쳐야 잡히고, 임베딩은 표현이 달라도")
    print("의미가 같으면 잡는다. 임베딩 쪽 임계값을 낮추면 서로 다른 문서까지")
    print("묶이기 시작하므로, 실제로 묶인 쌍을 눈으로 확인하고 정하는 것이 안전하다.")
