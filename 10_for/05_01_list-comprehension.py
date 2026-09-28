a = [1, 2, 3, 4]

# 방법 1 — 전통적인 for 루프
result = []
for num in a:
    result.append(num * 3)
print(result)

# 방법 2 — 리스트 컴프리헨션
result2 = [num * 3 for num in a]
print(result2)
