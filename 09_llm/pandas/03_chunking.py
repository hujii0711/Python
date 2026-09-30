"""03. 청킹 — 문서 1건을 청크 N건으로 펼치기

RAG 는 문서가 아니라 청크 단위로 검색한다.
핵심 도구는 explode: 리스트 컬럼을 행으로 펼쳐 1:N 관계를 만든다.
"""

import pandas as pd

docs = pd.DataFrame(
    {
        "doc_id": ["D1", "D2", "D3"],
        "title": ["파이썬 기초", "판다스 입문", "짧은 글"],
        "body": [
            "리스트는 순서가 있는 자료형입니다. 대괄호로 만듭니다. "
            "인덱싱과 슬라이싱이 가능합니다. reversed() 로 뒤집을 수 있습니다.",
            "판다스는 표 형태 데이터를 다룹니다. DataFrame 이 핵심 자료구조입니다. "
            "read_csv 로 파일을 읽습니다.",
            "한 문장뿐입니다.",
        ],
        "category": ["python", "pandas", "etc"],
    }
)


def split_sentences(text, size=2):
    """문장 단위로 자른 뒤 size 개씩 묶는다 (아주 단순한 청킹)."""
    sentences = [s.strip() + "." for s in text.split(".") if s.strip()]
    return [" ".join(sentences[i : i + size]) for i in range(0, len(sentences), size)]


# --- 1) 청크 리스트 컬럼 만들기 ---
docs["chunks"] = docs["body"].map(lambda t: split_sentences(t, size=2))
print("-- 청크 리스트 컬럼 --")
print(docs[["doc_id", "chunks"]].to_string(index=False))
print("\n문서별 청크 수:", docs["chunks"].str.len().tolist())

# --- 2) explode 로 행으로 펼치기 ---
# 문서의 다른 컬럼(title, category)은 자동으로 복제된다. 이게 explode 의 핵심 가치다.
chunks = docs.explode("chunks", ignore_index=True).rename(columns={"chunks": "text"})
print(f"\n-- explode 후: 문서 {len(docs)}건 -> 청크 {len(chunks)}건 --")
print(chunks[["doc_id", "category", "text"]].to_string(index=False))

# --- 3) 청크 ID 부여 ---
# 문서 내 순번을 매긴다. groupby.cumcount() 가 정석.
chunks["chunk_no"] = chunks.groupby("doc_id").cumcount()
chunks["chunk_id"] = chunks["doc_id"] + "-c" + chunks["chunk_no"].astype(str)

# 벡터DB 의 point id 는 정수나 UUID 여야 하므로 정수 id 도 같이 만든다
chunks["point_id"] = range(len(chunks))

print("\n-- ID 부여 --")
print(chunks[["point_id", "chunk_id", "doc_id", "chunk_no"]].to_string(index=False))

# --- 4) 토큰 길이 추정과 과대/과소 청크 점검 ---
# 정확한 토큰 수는 토크나이저가 필요하지만, 한국어는 문자수/1.5 정도로 거칠게 어림할 수 있다.
chunks["n_chars"] = chunks["text"].str.len()
chunks["est_tokens"] = (chunks["n_chars"] / 1.5).round().astype(int)

print("\n-- 청크 길이 분포 --")
print(chunks[["chunk_id", "n_chars", "est_tokens"]].to_string(index=False))
print("\n요약:")
print(chunks["n_chars"].describe().round(1).to_string())

MAX_TOKENS = 60
too_long = chunks[chunks["est_tokens"] > MAX_TOKENS]
print(f"\n{MAX_TOKENS} 토큰 초과 청크: {too_long['chunk_id'].tolist() or '없음'}")

# --- 5) 오버랩 청킹 ---
# 청크 경계에서 문맥이 끊기는 걸 막으려고 앞 청크의 끝을 조금 겹친다.
def chunk_with_overlap(text, size=40, overlap=10):
    """문자 기준 슬라이딩 윈도우. 실제로는 토큰 기준으로 하는 게 정석이다."""
    step = size - overlap
    return [text[i : i + size] for i in range(0, max(len(text) - overlap, 1), step)]


ov = docs[["doc_id", "body"]].copy()
ov["chunks"] = ov["body"].map(lambda t: chunk_with_overlap(t, 40, 10))
ov = ov.explode("chunks", ignore_index=True)
ov["chunk_no"] = ov.groupby("doc_id").cumcount()

print("\n-- 오버랩 청킹 (D1) --")
for row in ov[ov["doc_id"] == "D1"].itertuples():
    print(f"  c{row.chunk_no}: {row.chunks!r}")
print("  앞 청크의 끝 10자가 다음 청크 앞에 반복된다.")

# --- 6) explode 의 함정 ---
print("\n-- explode 함정 --")
# 빈 리스트는 NaN 행 하나를 남긴다. 임베딩 전에 반드시 걸러야 한다.
edge = pd.DataFrame({"doc_id": ["E1", "E2"], "chunks": [[], ["내용 있음"]]})
exploded = edge.explode("chunks", ignore_index=True)
print(exploded)
print(f"빈 리스트가 NaN 행을 만든다 -> dropna 필요: {exploded['chunks'].isna().sum()}건")
print("\n또한 ignore_index=False 면 인덱스가 중복된다:")
print(edge.explode("chunks").index.tolist(), "<- 임베딩 배열과 매칭할 때 사고가 난다")
