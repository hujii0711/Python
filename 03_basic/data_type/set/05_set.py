# 집합 연산
a = {1, 2, 3}
b = {2, 3, 4}
print(a | b)  # 합집합 {1, 2, 3, 4}
print(a & b)  # 교집합 {2, 3}
print(a - b)  # 차집합 {1}

set_a = {1, 2, 3, 4, 5}
set_b = {4, 5, 6, 7, 8}

# ① 교집합 (둘 다 있는 것)
print(set_a & set_b)  # 출력: {4, 5}
print(set_a.intersection(set_b))

# ② 합집합 (전체 합치기)
print(set_a | set_b)  # 출력: {1, 2, 3, 4, 5, 6, 7, 8}
print(set_a.union(set_b))

# ③ 차집합 (A에서 B를 빼기)
print(set_a - set_b)  # 출력: {1, 2, 3}
print(set_a.difference(set_b))

# ④ 대칭차집합 (서로 겹치지 않는 나머지 전체)
print(set_a ^ set_b)  # 출력: {1, 2, 3, 6, 7, 8}
