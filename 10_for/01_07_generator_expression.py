# 조건문 활용
# 리스트 컴프리헨션처럼 `if` 조건을 붙일 수 있습니다.
gen = (x for x in range(10) if x % 2 == 0)
print(list(gen))  # [0, 2, 4, 6, 8]
