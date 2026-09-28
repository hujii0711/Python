"""
제너레이터 순회
"""


def count_up(n):
    for i in range(n):
        yield i


# for문으로 순회 (가장 일반적)
for num in count_up(5):
    print(num)  # 0, 1, 2, 3, 4

# list로 변환
print(list(count_up(5)))  # [0, 1, 2, 3, 4]

# next()로 하나씩
gen = count_up(3)
print(next(gen))  # 0
print(next(gen))  # 1
