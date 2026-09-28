"""
step 활용
"""

print(list(range(0, 20, 5)))  # [0, 5, 10, 15]
print(list(range(10, 0, -1)))  # [10, 9, 8, ..., 1] (역순)
print(list(range(10, 0, -3)))  # [10, 7, 4, 1]
print(list(range(5, 0)))  # [] (step이 양수인데 start > stop이면 빈 결과)
