"""예제 4: 청킹 + 길이 분포 분석.

청크 크기는 RAG 품질에 가장 크게 영향을 주는 설정인데, 감으로 정하는 경우가 많다.
여기서는 후보 설정을 여러 개 돌려 분포를 비교하고 하나를 골라 저장한다.

보는 지표
  - 글자 수와 토큰 수 분포 (임베딩 모델 입력 한계는 토큰 기준이다)
  - 너무 짧은 청크  : 문맥이 없어 검색돼도 쓸모가 없다
  - 너무 긴 청크    : 모델 입력 한계를 넘으면 뒤가 잘린다
  - 문서당 청크 수  : 한 문서가 지나치게 잘게 쪼개지지 않았는지
"""

import pandas as pd
from langchain_text_splitters import RecursiveCharacterTextSplitter

from _common import (
    CHUNKS,
    CORPUS_DEDUP,
    EMBED_MODEL,
    read_jsonl,
    require,
    setup_console,
    write_jsonl,
)

# (chunk_size, chunk_overlap) 후보. 겹침은 보통 크기의 10~20% 를 쓴다.
CANDIDATES = [(300, 30), (500, 80), (800, 120)]
CHOSEN = (500, 80)

MIN_USEFUL_CHARS = 80    # 이보다 짧으면 문맥이 부족하다고 본다
MAX_MODEL_TOKENS = 8192  # bge-m3 입력 한계


def make_splitter(chunk_size: int, chunk_overlap: int) -> RecursiveCharacterTextSplitter:
    return RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        # 문단 -> 줄 -> 문장 순으로 끊어야 의미 단위가 덜 깨진다.
        separators=["\n\n", "\n", ". ", "다. ", " ", ""],
        length_function=len,
        add_start_index=True,
    )


def split_corpus(records: list[dict], chunk_size: int, overlap: int) -> list[dict]:
    splitter = make_splitter(chunk_size, overlap)
    chunks: list[dict] = []
    for record in records:
        pieces = splitter.split_text(record["text"])
        for index, piece in enumerate(pieces):
            chunks.append(
                {
                    "chunk_id": f"{record['doc_id']}::{index}",
                    "doc_id": record["doc_id"],
                    "source": record["source"],
                    "category": record["category"],
                    "chunk_index": index,
                    "text": piece,
                    "char_len": len(piece),
                }
            )
    return chunks


def count_tokens(texts: list[str]) -> list[int]:
    """임베딩 모델의 토크나이저로 실제 토큰 수를 센다.

    글자 수와 토큰 수는 비례하지 않는다. 한국어는 글자당 토큰이 영어보다 많이 나와서
    글자 기준으로만 자르면 모델 입력 한계를 넘길 수 있다.
    """
    from transformers import AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(EMBED_MODEL)
    encoded = tokenizer(texts, add_special_tokens=True)["input_ids"]
    return [len(ids) for ids in encoded]


if __name__ == "__main__":
    setup_console()

    require(CORPUS_DEDUP, "03_dedup.py")
    records = read_jsonl(CORPUS_DEDUP)
    print(f"입력: {len(records)}건 ({CORPUS_DEDUP.name})\n")

    # --- 후보 설정 비교 ---------------------------------------------------
    print("-- 청크 크기 후보 비교 --")
    rows = []
    for size, overlap in CANDIDATES:
        chunks = split_corpus(records, size, overlap)
        lengths = pd.Series([c["char_len"] for c in chunks])
        rows.append(
            {
                "chunk_size": size,
                "overlap": overlap,
                "청크수": len(chunks),
                "평균길이": round(lengths.mean()),
                "중앙값": int(lengths.median()),
                "최소": int(lengths.min()),
                "최대": int(lengths.max()),
                f"{MIN_USEFUL_CHARS}자미만": int((lengths < MIN_USEFUL_CHARS).sum()),
            }
        )
    print(pd.DataFrame(rows).to_string(index=False))

    # --- 고른 설정으로 저장 -----------------------------------------------
    size, overlap = CHOSEN
    chunks = split_corpus(records, size, overlap)
    print(f"\n선택: chunk_size={size}, overlap={overlap}")

    print("토큰 수 세는 중...")
    token_lens = count_tokens([c["text"] for c in chunks])
    for chunk, token_len in zip(chunks, token_lens):
        chunk["token_len"] = token_len

    frame = pd.DataFrame(chunks)

    print("\n-- 길이 분포 --")
    stats = frame[["char_len", "token_len"]].describe(
        percentiles=[0.25, 0.5, 0.75, 0.95]
    )
    print(stats.round(1).to_string())

    ratio = frame["char_len"].sum() / frame["token_len"].sum()
    print(f"\n토큰 1개당 평균 {ratio:.2f}자 "
          f"(한국어는 보통 1~2자. 글자 수로만 자르면 안 되는 이유다)")

    print("\n-- 이상 청크 --")
    too_short = frame[frame["char_len"] < MIN_USEFUL_CHARS]
    too_long = frame[frame["token_len"] > MAX_MODEL_TOKENS]
    print(f"  {MIN_USEFUL_CHARS}자 미만        : {len(too_short)}개")
    for _, row in too_short.iterrows():
        preview = row["text"][:40].replace("\n", " ")
        print(f"      {row['chunk_id']} ({row['char_len']}자) {preview}")
    print(f"  {MAX_MODEL_TOKENS}토큰 초과   : {len(too_long)}개 (초과분은 뒤가 잘린다)")

    print("\n-- 문서당 청크 수 --")
    per_doc = frame.groupby("doc_id").size().sort_values(ascending=False)
    print(per_doc.head(5).to_string())
    print(f"  ... 전체 {len(per_doc)}개 문서, 평균 {per_doc.mean():.1f}개")

    written = write_jsonl(CHUNKS, chunks)
    print(f"\n청크 {written}개 -> {CHUNKS.name}")
