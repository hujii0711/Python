"""
리스트 인덱스 순회
"""

fruits = ["사과", "바나나", "체리"]

for i in range(len(fruits)):
    print(i, fruits[i])

# 인덱스와 값이 모두 필요하면 enumerate가 더 파이썬답습니다
for i, fruit in enumerate(fruits):
    print(i, fruit)

# 역순 순회
for i in range(len(fruits) - 1, -1, -1):
    print(fruits[i])
# 더 간단하게: for fruit in reversed(fruits)
