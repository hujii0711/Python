"""
리스트 컴플리헨션
"""

squares = [x**2 for x in range(1, 6)]
print(squares)  # [1, 4, 9, 16, 25]

evens = [x for x in range(10) if x % 2 == 0]
print(evens)  # [0, 2, 4, 6, 8]

# 조건 표현식
labels = ["짝수" if x % 2 == 0 else "홀수" for x in range(5)]
print(labels)  # ['짝수', '홀수', '짝수', '홀수', '짝수']

# 2중 반복 (평탄화)
matrix = [[1, 2], [3, 4], [5, 6]]
flat = [n for row in matrix for n in row]
print(flat)  # [1, 2, 3, 4, 5, 6]
