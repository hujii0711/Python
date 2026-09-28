"""
파이썬에서 `for ... in` 문에 사용할 수 있는 객체들을 반복 가능한 객체(Iterable)라고 부릅니다.
쉽게 말해, 내부 요소들을 한 개씩 차례대로 꺼낼 수 있는 데이터 타입들을 의미합니다.
1) 리스트
2) 튜플
3) 문자열
4) 딕셔너리
5) set
"""

# 리스트 순회
for item in [1, 2, 3]:
    print(item)

# 튜플 순회
for item in ("A", "B", "C"):
    print(item)

# 문자열 순회
for char in "Python":
    print(char)  # P, y, t, h, o, n이 한 줄씩 출력됨

# 딕셔너리 순회
my_dict = {"name": "Alice", "age": 25}

for key in my_dict:  # 키 순회
    print(key)

for val in my_dict.values():  # 값 순회
    print(val)

# set 순회
# 중복을 허용하지 않는 집합 타입도 순회가 가능합니다. 단, 집합은 **순서가 없기 때문에** 출력되는 순서가 매번 달라질 수 있습니다.
for num in (1, 2, 3):  # 중복은 제거됨
    print(num)
