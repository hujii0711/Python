# 특징 3: `next()`로 값을 하나씩 꺼내기
gen = (x**2 for x in range(3))

print(next(gen))  # 0
print(next(gen))  # 1
print(next(gen))  # 4
print(next(gen))  # StopIteration 에러 (더 이상 값 없음)
