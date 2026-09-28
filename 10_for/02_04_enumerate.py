"""
사용 가능한 자료형
1) `list` (리스트)
2) `tuple` (튜플)
3) `str` (문자열)
4) `set` (집합)
5) `range`
6) `dict` (딕셔너리)
"""

# 1 리스트
for i, v in enumerate(["a", "b", "c"]):
    print(i, v)

# 2 튜플
colors = ("빨강", "초록", "파랑")

for i, color in enumerate(colors):
    print(i, color)

students = [("철수", 85), ("영희", 92), ("민수", 78)]

# 튜플2
for i, (name, score) in enumerate(students):
    print(f"{i}: 이름={name}, 점수={score}")

# 3 문자열
for i, c in enumerate("hello"):
    print(i, c)

# 4 set
for i, v in enumerate({10, 20, 30}):
    print(i, v)

# 5 range
for i, num in enumerate(range(5)):
    print(i, num)

for i, num in enumerate(range(10, 15)):
    print(f"인덱스={i}, 값={num}")

# 6 딕셔너리 (key를 순회)
for i, k in enumerate({"x": 1, "y": 2}):
    print(i, k)

# 딕셔너리로 변환하기
color_dict = {i: color for i, color in enumerate(colors)}
print(color_dict)
