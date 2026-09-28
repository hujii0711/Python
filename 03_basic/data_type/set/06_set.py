# 딕셔너리 컴프리헨션
squares = {x: x**2 for x in range(5)}
# {0: 0, 1: 1, 2: 4, 3: 9, 4: 16}

# 집합 컴프리헨션
unique_squares = {x**2 for x in range(-3, 4)}
# {0, 1, 4, 9}
