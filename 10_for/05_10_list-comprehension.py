"""
컴프리헨션의 for는 일반 반복문을 쓸 때와 같은 순서로 왼쪽에서 오른쪽으로 읽습니다. 맨 앞의 x는 결과에 담길 값입니다.
"""

# 중첩 ⑥
# 이중 for문 (2차원 → 1차원)
# 리스트 안의 리스트를 하나로 펼칩니다.
matrix = [[1, 2], [3, 4], [5, 6]]
a = [row for row in matrix]
print("a====", a)

# [x for row in matrix for x in row]
#  ↑      └── 바깥 ──┘ └─ 안쪽 ─┘
# 결과값
flat = [x for row in matrix for x in row]
print(flat)
# → [1, 2, 3, 4, 5, 6]

# 일반 for문으로 풀면
flat = []
for row in matrix:  # 바깥 반복
    for x in row:  # 안쪽 반복
        flat.append(x)  # 맨 앞의 x

# 짝수만 평탄화
print([x for row in matrix for x in row if x % 2 == 0])  # [2, 4, 6]

# 값을 변환하면서 평탄화
print([x * 10 for row in matrix for x in row])  # [10, 20, 30, 40, 50, 60]

# 행 단위로 조건 걸기 (첫 원소가 1보다 큰 행만)
print([x for row in matrix if row[0] > 1 for x in row])  # [3, 4, 5, 6]

# 평탄화하지 않고 각 요소만 변환, for를 하나만 쓰면 구조가 유지됩니다.
print([[x * 2 for x in row] for row in matrix])
# [[2, 4], [6, 8], [10, 12]]
