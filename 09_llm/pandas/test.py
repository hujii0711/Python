import pandas as pd

df = pd.DataFrame(
    {
        "name": ["철수", "영희", "민수", "지수", "현우"],
        "age": [25, 30, 22, 28, 35],
        "city": ["서울", "부산", "서울", "대구", "부산"],
        "salary": [3500, 4200, 3000, 3800, 5000],
    }
)
print(df)
#   name  age city  salary
# 0   철수   25   서울    3500
# 1   영희   30   부산    4200
# 2   민수   22   서울    3000
# 3   지수   28   대구    3800
# 4   현우   35   부산    5000

# 딕셔너리 리스트로도 생성 가능
df2 = pd.DataFrame([{"a": 1, "b": 2}, {"a": 3, "b": 4}])

# Series (1차원)
s = pd.Series([10, 20, 30], index=["a", "b", "c"])
print(s["b"])  # 20
