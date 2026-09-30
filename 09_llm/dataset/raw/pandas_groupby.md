# 판다스 그룹 집계와 성능

## 기본 그룹 집계

`df.groupby("category")["price"].mean()` 이 기본 형태다.
여러 집계를 한 번에 하려면 `agg({"price": ["mean", "max"], "qty": "sum"})` 를 쓴다.
집계 결과의 열 이름이 복잡해지면 `reset_index()` 로 평평하게 펴는 편이 다루기 쉽다.

## transform 과 filter

그룹 결과를 원본 행 수 그대로 붙이려면 `transform` 을 쓴다.
그룹 평균과의 차이를 구하는 식은 `df["price"] - df.groupby("c")["price"].transform("mean")` 이다.
조건을 만족하는 그룹만 남기려면 `filter(lambda g: len(g) >= 10)` 을 쓴다.

## 성능 팁

`iterrows()` 반복은 느리다. 벡터 연산이나 `apply` 로 바꾸는 편이 빠르다.
문자열 열은 `astype("category")` 로 바꾸면 메모리를 크게 줄일 수 있다.
큰 CSV 는 `chunksize` 로 나눠 읽어서 부분 집계를 누적한다.
`query()` 와 `eval()` 은 중간 객체를 덜 만들어서 큰 데이터에서 유리하다.
