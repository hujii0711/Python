"""01. 문서 코퍼스 로딩 — dtype / 인코딩 / 결측

RAG 파이프라인의 첫 단계. 여기서 dtype 을 잘못 잡으면 뒤의 모든 단계가 느려진다.
pandas 3.0 부터 문자열 기본 dtype 이 object 가 아니라 str 이다.
"""

import io

import pandas as pd

print("pandas:", pd.__version__)

# --- CSV 로 들어온 문서 코퍼스 ---
csv_text = """doc_id,title,body,category,published,views
D001,파이썬 리스트 뒤집기,리스트를 뒤집는 방법은 reversed() 또는 [::-1] 입니다.,python,2026-01-15,1200
D002,판다스 CSV 읽기,read_csv 로 파일을 읽습니다.,pandas,2026-02-03,890
D003,,본문만 있고 제목이 없는 문서,python,2026-02-20,450
D004,빈 본문 문서,,etc,2026-03-01,12
D005,중복 문서,리스트를 뒤집는 방법은 reversed() 또는 [::-1] 입니다.,python,2026-03-11,330
"""

df = pd.read_csv(io.StringIO(csv_text))
print("\n-- 기본 로딩 --")
print(df)
print("\ndtypes:")
print(df.dtypes)
print("\npandas 3.0 에서 문자열은 object 가 아니라 str dtype 이다 ->", df["body"].dtype)

# --- dtype 을 명시해서 읽기 ---
# category 는 값 종류가 적을 때 메모리를 크게 줄인다. 날짜는 parse_dates 로 한 번에.
df = pd.read_csv(
    io.StringIO(csv_text),
    dtype={"doc_id": "str", "category": "category", "views": "int32"},
    parse_dates=["published"],
)
print("\n-- dtype 명시 후 --")
print(df.dtypes)

# --- 결측 확인: 임베딩 전에 반드시 봐야 한다 ---
print("\n-- 결측치 --")
print(df.isna().sum())
print("\n제목 없는 문서:", df.loc[df["title"].isna(), "doc_id"].tolist())
print("본문 없는 문서:", df.loc[df["body"].isna(), "doc_id"].tolist())

# 본문이 없으면 임베딩할 내용이 없다. 영벡터가 되어 검색을 오염시킨다(numpy 05 예제 참고).
before = len(df)
df = df.dropna(subset=["body"]).copy()
print(f"\n본문 없는 문서 제거: {before} -> {len(df)}")

# 제목 결측은 빈 문자열로 채워도 된다 (임베딩 텍스트를 조립할 때 쓰므로)
df["title"] = df["title"].fillna("")

# --- 임베딩에 넣을 텍스트 조립 ---
# 제목과 본문을 합치면 검색 품질이 올라가는 경우가 많다.
df["embed_text"] = (df["title"] + "\n" + df["body"]).str.strip()
print("\n-- 임베딩 입력 텍스트 --")
for row in df.itertuples():
    print(f"  {row.doc_id}: {row.embed_text[:40]!r}")

# --- 메모리 확인 ---
print("\n-- 메모리 사용량 --")
print(df.memory_usage(deep=True))
print(f"합계: {df.memory_usage(deep=True).sum():,} bytes")

# --- JSONL 로 들어오는 경우 ---
# 문서 코퍼스는 JSONL 이 흔하다. lines=True 를 잊지 말 것.
jsonl = '\n'.join([
    '{"doc_id": "D101", "body": "첫 줄 문서", "meta": {"lang": "ko"}}',
    '{"doc_id": "D102", "body": "둘째 줄 문서", "meta": {"lang": "en"}}',
])
jdf = pd.read_json(io.StringIO(jsonl), lines=True)
print("\n-- JSONL --")
print(jdf)
print("중첩 dict 컬럼의 dtype:", jdf["meta"].dtype, "<- 평탄화가 필요하다")

# 중첩 구조는 json_normalize 로 펼친다
flat = pd.json_normalize(jdf.to_dict("records"))
print("\njson_normalize 후 컬럼:", list(flat.columns))
