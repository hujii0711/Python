"""예제 5: 메타데이터 보강.

청크 본문만으로는 필터도 못 걸고 문제 진단도 어렵다. 검색 시점에 쓸 필드와
데이터 품질을 확인할 필드를 미리 계산해 붙여둔다.

붙이는 필드
  section        : 청크가 속한 마크다운 제목 (근거를 사람에게 보여줄 때 쓴다)
  heading_path   : 상위 제목까지 포함한 경로 (문서 > 절)
  hangul_ratio   : 한글 비율. 언어 판별과 코드 덩어리 탐지에 쓴다
  has_code       : 백틱 코드가 들어 있는지
  is_table_like  : 표나 목록 위주인지 (문장이 아니라 검색 품질이 다르게 나온다)
  position       : 문서 안에서의 상대 위치 0.0 ~ 1.0
  lang           : ko / en / mixed
"""

import re

from _common import (
    CHUNKS,
    CHUNKS_ENRICHED,
    char_profile,
    read_jsonl,
    require,
    setup_console,
    write_jsonl,
)

HEADING = re.compile(r"^(#{1,6})\s+(.*)$", re.MULTILINE)
CODE_SPAN = re.compile(r"`[^`]+`|```")
LIST_OR_TABLE = re.compile(r"^\s*([-*+]|\d+\.|\|)", re.MULTILINE)


def apply_heading(path: list[str], hashes: str, title: str) -> list[str]:
    """제목 하나를 경로에 반영한다. 깊이(#의 개수)만큼 상위를 유지하고 끝을 교체한다."""
    level = len(hashes)
    path = path[: level - 1]
    while len(path) < level - 1:
        path.append("")
    return path + [title.strip()]


def heading_path(text: str, previous: list[str]) -> tuple[str, list[str]]:
    """이 청크의 heading 경로와, 다음 청크에 물려줄 경로를 함께 돌려준다.

    청크가 여러 절에 걸쳐 있으면 경로가 두 개 필요하다.
      - 이 청크의 대표 : 청크 안의 첫 제목. 마지막 제목을 쓰면 청크 앞부분 내용이
        엉뚱한 절에 속한 것처럼 기록된다.
      - 다음에 물려줄 것 : 청크 안의 마지막 제목까지 반영한 경로.
    제목이 아예 없는 청크는 앞 청크의 경로를 그대로 이어받는다.
    """
    found = HEADING.findall(text)
    if not found:
        return (" > ".join(p for p in previous if p), list(previous))

    own = apply_heading(list(previous), *found[0])
    carry = list(previous)
    for hashes, title in found:
        carry = apply_heading(carry, hashes, title)
    return (" > ".join(p for p in own if p), carry)


def classify_lang(profile: dict[str, float]) -> str:
    """글자 비율로 대충 판별한다. 정확한 판별이 필요하면 전용 라이브러리를 쓴다."""
    hangul, latin = profile["hangul_ratio"], profile["latin_ratio"]
    if hangul >= 0.15 and latin >= 0.15:
        return "mixed"
    if hangul >= latin:
        return "ko"
    return "en"


if __name__ == "__main__":
    setup_console()

    require(CHUNKS, "04_chunk_and_stats.py")
    chunks = read_jsonl(CHUNKS)
    print(f"입력: {len(chunks)}개 청크 ({CHUNKS.name})\n")

    # 문서별 청크 총 개수를 알아야 상대 위치를 계산할 수 있다.
    total_per_doc: dict[str, int] = {}
    for chunk in chunks:
        total_per_doc[chunk["doc_id"]] = total_per_doc.get(chunk["doc_id"], 0) + 1

    enriched: list[dict] = []
    heading_state: dict[str, list[str]] = {}

    for chunk in sorted(chunks, key=lambda c: (c["doc_id"], c["chunk_index"])):
        doc_id = chunk["doc_id"]
        text = chunk["text"]

        # path_str 은 이 청크의 경로, carry 는 다음 청크에 물려줄 경로다.
        path_str, carry = heading_path(text, heading_state.get(doc_id, []))
        heading_state[doc_id] = carry

        profile = char_profile(text)
        total = total_per_doc[doc_id]
        position = chunk["chunk_index"] / max(total - 1, 1)

        enriched.append(
            {
                **chunk,
                # section 은 반드시 heading_path 의 마지막 요소와 같아야 한다.
                # carry 에서 뽑으면 청크에 없는 절 이름이 붙는다.
                "section": path_str.split(" > ")[-1] if path_str else "",
                "heading_path": path_str,
                **profile,
                "lang": classify_lang(profile),
                "has_code": bool(CODE_SPAN.search(text)),
                "is_table_like": len(LIST_OR_TABLE.findall(text)) >= 3,
                "position": round(position, 3),
                "doc_chunk_total": total,
            }
        )

    written = write_jsonl(CHUNKS_ENRICHED, enriched)
    print(f"보강 완료 {written}개 -> {CHUNKS_ENRICHED.name}\n")

    print("-- 언어 분포 --")
    by_lang: dict[str, int] = {}
    for chunk in enriched:
        by_lang[chunk["lang"]] = by_lang.get(chunk["lang"], 0) + 1
    for lang, count in sorted(by_lang.items()):
        print(f"  {lang:<6} {count}개")

    code_count = sum(1 for c in enriched if c["has_code"])
    table_count = sum(1 for c in enriched if c["is_table_like"])
    print(f"\n코드 포함 청크 : {code_count}개")
    print(f"목록/표 위주   : {table_count}개")

    print("\n-- heading_path 예시 --")
    for chunk in enriched[:8]:
        path = chunk["heading_path"] or "(제목 없음)"
        print(f"  {chunk['chunk_id']:<22} {path}")

    print("\n-- 한글 비율이 낮은 청크 (코드나 영문 위주일 가능성) --")
    low = sorted(enriched, key=lambda c: c["hangul_ratio"])[:3]
    for chunk in low:
        preview = chunk["text"][:45].replace("\n", " ")
        print(f"  {chunk['hangul_ratio']:.2f}  {chunk['chunk_id']:<22} {preview}")
