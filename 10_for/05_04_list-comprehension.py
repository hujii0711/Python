a = [1, 2, 3, 4]

# 조건 필터링 — 홀수만
result = []
for num in a:  # 첫 번째 for
    if num % 2 == 0:  # 첫 번째 if (짝수만 통과)
        for num in a:  # 두 번째 for (여기서 num이 덮어씌워짐!)
            if num % 2 == 1:  # 두 번째 if (홀수만 통과)
                result.append(num * 3)
print(result)

result2 = [num * 3 for num in a if num % 2 == 1]
print(result2)


result3 = [num * 3 for num in a if num % 2 == 0 for num in a if num % 2 == 1]
print(result3)
