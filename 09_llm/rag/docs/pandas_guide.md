# 판다스 사용 가이드

## CSV 읽고 쓰기

`pd.read_csv("data.csv")` 로 읽는다.
한글이 깨지면 `encoding="utf-8-sig"` 또는 `encoding="cp949"` 를 지정한다.
열 이름이 없는 파일은 `header=None, names=[...]` 로 직접 붙인다.
저장은 `df.to_csv("out.csv", index=False)` 처럼 인덱스를 빼는 편이 깔끔하다.

## 결측치 처리

`df.isna().sum()` 으로 열별 결측치 개수를 센다.
`df.fillna(0)` 은 고정값으로 채우고, `df.fillna(df.mean())` 은 평균으로 채운다.
시계열이면 `df.ffill()` 로 직전 값을 끌어오는 방식이 자연스럽다.
결측 행을 버릴 때는 `df.dropna(subset=["price"])` 처럼 대상 열을 좁힌다.

## 그룹 집계

`df.groupby("category")["price"].mean()` 이 기본 형태다.
여러 집계를 한 번에 하려면 `agg({"price": ["mean", "max"], "qty": "sum"})` 를 쓴다.
그룹 결과를 원본 행 수 그대로 붙이려면 `transform` 을 쓴다.

## 성능 팁

`iterrows()` 반복은 느리다. 벡터 연산이나 `apply` 로 바꾸는 편이 빠르다.
문자열 열은 `astype("category")` 로 바꾸면 메모리를 크게 줄일 수 있다.
큰 CSV 는 `chunksize` 로 나눠 읽어서 부분 집계를 누적한다.
