a = [1, 2, 3, 4]

# 조건 필터링 — 짝수만
result = []
for num in a:
    if num % 2 == 0:
        result.append(num * 3)
print(result)

result2 = [num * 3 for num in a if num % 2 == 0]
print(result2)
