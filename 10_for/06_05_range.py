"""
컴프리헨션과 함께
"""

print([x**2 for x in range(1, 6)])  # [1, 4, 9, 16, 25]
print([x for x in range(20) if x % 3 == 0])  # [0, 3, 6, 9, 12, 15, 18]
print(sum(range(1, 101)))  # 5050

# 구구단
for i in range(1, 10):
    print(f"3 x {i} = {3 * i}")

# 2차원 리스트 만들기
grid = [[0] * 3 for _ in range(3)]

# 이중 반복
for i in range(1, 4):
    for j in range(1, 4):
        print(i * j, end=" ")
    print()
