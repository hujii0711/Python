"""예제 2: 텍스트 정제.

검색 품질을 떨어뜨리는 잡음을 걷어낸다. 정제는 되돌릴 수 없으므로 원본은 그대로 두고
새 파일로 저장하고, 각 규칙이 무엇을 얼마나 바꿨는지 기록해서 과하게 지우지 않았는지 본다.

여기서 다루는 잡음
  - HTML 태그, script/style 블록, 엔티티
  - 머리말/꼬리말 보일러플레이트 (문서마다 반복되는 줄)
  - 전각 문자, 제어 문자, BOM
  - 중복 공백, 연속 빈 줄, 줄 앞뒤 공백
  - 너무 짧아 정보가 없는 문서

제목 구조는 지우지 않고 마크다운으로 옮긴다. HTML 의 h1~h6 를 그냥 태그로 취급해
날려버리면 "이 문단이 어느 절에 속하는지" 를 뒤 단계에서 복원할 수 없다.
"""

import re

from _common import (
    CORPUS_CLEAN,
    CORPUS_RAW,
    normalize_unicode,
    read_jsonl,
    require,
    setup_console,
    sha256_text,
    write_jsonl,
)

MIN_CHARS = 50  # 이보다 짧은 문서는 버린다

# 문서마다 반복되는 머리말/꼬리말. 실무에서는 "여러 문서에 공통으로 나오는 줄"을
# 자동으로 찾아 제거하지만, 여기서는 규칙을 눈에 보이게 적어둔다.
BOILERPLATE_PATTERNS = [
    re.compile(r"^=+.*=+$"),       # === 사내 기술문서 · 대외비 ===
    re.compile(r"^-\s*\d+\s*-$"),  # - 1 -  (페이지 번호)
    re.compile(r"^\s*©.*$"),       # © 2026 사내 위키
]

SCRIPT_STYLE = re.compile(r"<(script|style)\b.*?</\1>", re.IGNORECASE | re.DOTALL)
HTML_HEADING = re.compile(r"<h([1-6])\b[^>]*>(.*?)</h\1>", re.IGNORECASE | re.DOTALL)
INNER_TAG = re.compile(r"<[^>]+>")

# 블록 태그는 줄바꿈으로 바꿔야 문단이 서로 붙지 않는다. 나머지 인라인 태그는 그냥 지운다.
BLOCK_TAG = re.compile(
    r"</?(p|div|br|hr|li|ul|ol|tr|table|section|article"
    r"|nav|header|footer|body|head|html)\b[^>]*>",
    re.IGNORECASE,
)

CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
MULTI_SPACE = re.compile(r"[ \t]+")
MULTI_BLANK_LINE = re.compile(r"\n{3,}")

# &amp; 를 먼저 풀면 "&amp;lt;" 같은 이중 인코딩이 꼬이므로 맨 마지막에 처리한다.
HTML_ENTITIES = [
    ("&nbsp;", " "),
    ("&lt;", "<"),
    ("&gt;", ">"),
    ("&quot;", '"'),
    ("&#39;", "'"),
    ("&copy;", "©"),
    ("&amp;", "&"),
]


def heading_to_markdown(match: re.Match) -> str:
    """<h2>제목</h2> -> '## 제목'. 문서 구조를 잃지 않도록 먼저 변환한다."""
    level = int(match.group(1))
    title = INNER_TAG.sub("", match.group(2)).strip()
    return "\n" + "#" * level + " " + title + "\n"


def strip_html(text: str) -> str:
    """순서가 중요하다.

    1. script/style 블록을 통째로 지운다. 태그만 먼저 지우면 코드가 본문으로 남는다.
    2. h1~h6 를 마크다운 제목으로 바꾼다. 구조를 남기기 위해서다.
    3. 블록 태그는 줄바꿈으로, 나머지 인라인 태그는 삭제한다.
    """
    text = SCRIPT_STYLE.sub("\n", text)
    text = HTML_HEADING.sub(heading_to_markdown, text)
    text = BLOCK_TAG.sub("\n", text)
    text = INNER_TAG.sub("", text)
    for entity, char in HTML_ENTITIES:
        text = text.replace(entity, char)
    return text


def drop_boilerplate(text: str) -> str:
    kept = [
        line
        for line in text.split("\n")
        if not any(pattern.match(line.strip()) for pattern in BOILERPLATE_PATTERNS)
    ]
    return "\n".join(kept)


def normalize_whitespace(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = CONTROL_CHARS.sub("", text)
    text = MULTI_SPACE.sub(" ", text)
    text = "\n".join(line.strip() for line in text.split("\n"))
    text = MULTI_BLANK_LINE.sub("\n\n", text)
    return text.strip()


def clean(text: str, ext: str) -> tuple[str, dict[str, tuple[int, bool]]]:
    """정제한 본문과 규칙별 (줄어든 글자 수, 실제로 바뀌었는지) 를 함께 돌려준다.

    글자 수만 세면 NFKC 정규화처럼 길이가 그대로인 규칙이 아무 일도 안 한 것처럼
    보인다. 바뀌었는지 여부를 따로 기록해야 규칙이 동작하는지 확인할 수 있다.
    """
    steps: dict[str, tuple[int, bool]] = {}

    def apply(name, func, current):
        result = func(current)
        steps[name] = (len(current) - len(result), result != current)
        return result

    if ext == "html":
        text = apply("html", strip_html, text)

    text = apply("boilerplate", drop_boilerplate, text)
    text = apply("unicode", normalize_unicode, text)  # 전각 -> 반각
    text = apply("whitespace", normalize_whitespace, text)

    return text, steps


if __name__ == "__main__":
    setup_console()

    require(CORPUS_RAW, "01_build_corpus.py")
    records = read_jsonl(CORPUS_RAW)
    print(f"입력: {len(records)}건 ({CORPUS_RAW.name})\n")

    cleaned: list[dict] = []
    dropped: list[tuple[str, str]] = []
    total_saved: dict[str, int] = {}
    total_changed: dict[str, int] = {}

    for record in records:
        text, steps = clean(record["text"], record["ext"])
        for name, (saved, changed) in steps.items():
            total_saved[name] = total_saved.get(name, 0) + saved
            total_changed[name] = total_changed.get(name, 0) + int(changed)

        if len(text) < MIN_CHARS:
            dropped.append((record["doc_id"], f"{len(text)}자 < {MIN_CHARS}자"))
            continue

        cleaned.append(
            {
                **record,
                "text": text,
                "char_len": len(text),
                "sha256": sha256_text(text),  # 본문이 바뀌었으니 해시도 다시 계산
                "raw_char_len": record["char_len"],
            }
        )

    print("-- 규칙별 적용 결과 --")
    print(f"  {'규칙':<12}{'줄어든 글자':>12}{'바뀐 문서':>11}")
    for name, saved in sorted(total_saved.items(), key=lambda kv: -kv[1]):
        print(f"  {name:<12}{saved:>10}자{total_changed[name]:>10}건")

    print(f"\n-- 최소 길이({MIN_CHARS}자) 미달로 버린 문서: {len(dropped)}건 --")
    for doc_id, reason in dropped:
        print(f"  {doc_id} ({reason})")

    written = write_jsonl(CORPUS_CLEAN, cleaned)
    total_before = sum(r["raw_char_len"] for r in cleaned)
    total_after = sum(r["char_len"] for r in cleaned)
    print(f"\n남은 문서 {written}건 -> {CORPUS_CLEAN.name}")
    print(f"글자 수 {total_before} -> {total_after} "
          f"({(1 - total_after / total_before) * 100:.1f}% 감소)")

    sample = next(r for r in cleaned if r["ext"] == "html")
    print(f"\n-- 정제 예시: {sample['doc_id']} (HTML -> 마크다운 제목 보존) --")
    print(sample["text"][:300])
