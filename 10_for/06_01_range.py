"""
range는 정수 시퀀스를 만듭니다. 끝 값은 포함하지 않습니다.
range 객체는 값을 미리 다 만들지 않아서 range(10_000_000)도 메모리를 거의 쓰지 않습니다. 값을 눈으로 보려면 list()로 감싸야 합니다.
"""

print(list(range(5)))  # [0, 1, 2, 3, 4]      range(stop)
print(list(range(2, 7)))  # [2, 3, 4, 5, 6]      range(start, stop)
print(list(range(0, 10, 2)))  # [0, 2, 4, 6, 8]      range(start, stop, step)
