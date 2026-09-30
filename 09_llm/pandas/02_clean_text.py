"""02. 텍스트 정제 — .str 접근자와 Copy-on-Write

임베딩 품질은 입력 텍스트 품질을 넘지 못한다.

.str 접근자는 결측(NA)을 알아서 건너뛰고 체인이 읽기 쉬워 기본 선택지지만,
"벡터화니까 항상 빠르다"는 말은 사실이 아니다. 정규식 .str.replace 는 행마다
파이썬 정규식 엔진을 호출하므로 단순 split()/join() 보다 느릴 수 있다.
아래에서 실제로 측정한다.
"""

import time

import pandas as pd

df = pd.DataFrame(
    {
        "doc_id": ["D1", "D2", "D3", "D4", "D5", "D6"],
        "body": [
            "  파이썬에서   리스트를 뒤집는   방법  ",  # 중복 공백 + 앞뒤 공백
            "list\treverse\nin\r\npython",  # 탭/개행/CRLF
            "제로폭​문자와\xa0non-breaking space",  # 보이지 않는 문자
            "짧음",  # 너무 짧아 임베딩 가치가 없음
            "<p>HTML <b>태그</b>가 섞인 문서</p>",  # 마크업
            "정상적인 길이의 문서입니다. 이 문서는 충분한 내용을 담고 있습니다.",
        ],
    }
)

print("-- 원본 --")
for row in df.itertuples():
    print(f"  {row.doc_id}: {row.body!r}")

# --- 1) HTML 태그 제거 ---
df["clean"] = df["body"].str.replace(r"<[^>]+>", "", regex=True)

# --- 2) 보이지 않는 문자 제거 ---
# 제로폭 문자(​)와 non-breaking space(\xa0)는 눈에 안 보이면서 토큰을 늘린다.
df["clean"] = df["clean"].str.replace(r"[​‌‍﻿]", "", regex=True)
df["clean"] = df["clean"].str.replace("\xa0", " ", regex=False)

# --- 3) 모든 공백류를 단일 스페이스로 ---
# \s 는 탭/개행/CRLF 를 모두 포함한다. 이걸 한 번에 정리하는 게 핵심.
df["clean"] = df["clean"].str.replace(r"\s+", " ", regex=True).str.strip()

print("\n-- 정제 후 --")
for row in df.itertuples():
    print(f"  {row.doc_id}: {row.clean!r}")

# --- 4) 길이 기준 필터 ---
# 너무 짧은 청크는 검색 노이즈만 만든다. 문자 수와 단어 수를 함께 본다.
df["n_chars"] = df["clean"].str.len()
df["n_words"] = df["clean"].str.split().str.len()

print("\n-- 길이 --")
print(df[["doc_id", "n_chars", "n_words"]].to_string(index=False))

MIN_CHARS = 10
kept = df[df["n_chars"] >= MIN_CHARS]
dropped = df[df["n_chars"] < MIN_CHARS]
print(f"\n{MIN_CHARS}자 미만 제거: {dropped['doc_id'].tolist()} -> {len(kept)}건 남음")

# --- .str 벡터화 vs apply 속도 ---
big = pd.DataFrame({"body": ["  여러 공백이   들어간   문서  " * 3] * 50_000})

t0 = time.perf_counter()
vec = big["body"].str.replace(r"\s+", " ", regex=True).str.strip()
t_vec = time.perf_counter() - t0

t0 = time.perf_counter()
app = big["body"].apply(lambda s: " ".join(s.split()))
t_apply = time.perf_counter() - t0

print(f"\n-- 5만건 정제 속도 --")
print(f"  .str 체인 : {t_vec * 1000:7.1f} ms")
print(f"  apply     : {t_apply * 1000:7.1f} ms")
print(f"  결과 동일 : {vec.equals(app)}")
faster = ".str 체인" if t_vec < t_apply else "apply"
print(f"  -> 이 환경에서는 {faster} 가 빠르다 ({abs(t_apply / t_vec - 1):.0%} 차이)")
print("  정규식 .str.replace 는 행마다 re 엔진을 호출하므로 '벡터화'의 이득이 크지 않다.")
print("  .str 을 쓰는 진짜 이유는 속도가 아니라 결측(NA) 자동 처리와 체인 가독성이다.")
print("  apply 를 쓸 거면 결측을 직접 막아야 한다:")
with_na = pd.Series(["  공백  ", None])
print(f"    .str.strip()          -> {with_na.str.strip().tolist()}  (NA 유지)")
try:
    with_na.apply(lambda s: s.strip())
except AttributeError as exc:
    print(f"    apply(lambda s: s.strip()) -> AttributeError: {exc}")

# --- 흔한 실수: 정제 결과를 대입하지 않는다 ---
print("\n-- 흔한 실수 --")
sample = pd.DataFrame({"body": ["  공백  "]})
sample["body"].str.strip()  # 반환값을 버림. 원본은 그대로다
print(f"  대입 안 함: {sample['body'][0]!r} <- 안 바뀜")
sample["body"] = sample["body"].str.strip()
print(f"  대입 함  : {sample['body'][0]!r}")

# pandas 3.0 은 Copy-on-Write 가 항상 켜져 있어 chained assignment 가 조용히 실패한다.
sample2 = pd.DataFrame({"body": ["  공백  "]})
sample2["body"][0] = "직접 수정"  # 경고와 함께 무시되거나 에러가 난다
print(f"  chained assignment 결과: {sample2['body'][0]!r} <- 반영되지 않는다")
print("  -> .loc[행, 열] = 값 형태로 한 번에 지정해야 한다")
sample2.loc[0, "body"] = "loc 로 수정"
print(f"  .loc 사용: {sample2['body'][0]!r}")
