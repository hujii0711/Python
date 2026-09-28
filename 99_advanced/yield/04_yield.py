"""
return vs yield 메모리 차이
"""

import sys


# return - 100만개 리스트를 한번에 메모리에 올림
def use_return(n):
    return [i * 2 for i in range(n)]


# yield - 하나씩 그때그때 생성
def use_yield(n):
    for i in range(n):
        yield i * 2


result_return = use_return(1_000_000)
result_yield = use_yield(1_000_000)

print(sys.getsizeof(result_return))  # 8,448,728 bytes (약 8MB)
print(sys.getsizeof(result_yield))  # 104 bytes ← 제너레이터 객체만!
