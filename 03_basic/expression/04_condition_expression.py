# 조건 표현식(삼항 연산자)

# ④ 리스트 컴프리헨션과 함께
# 리스트를 만들면서 각 요소에 조건을 적용합니다.
nums = [1, 2, 3, 4, 5]
labels = ["짝" if n % 2 == 0 else "홀" for n in nums]
# → ["홀", "짝", "홀", "짝", "홀"]
print(labels)

# 위와 동일
labels2 = []
for n in nums:
    if n % 2 == 0:
        labels2.append("짝")
    else:
        labels2.append("홀")
print(labels2)
