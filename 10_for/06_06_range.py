"""
range 객체의 기능
"""

r = range(0, 10, 2)

print(len(r))  # 5
print(r[0], r[-1])  # 0 8 (인덱싱 가능)
print(r[1:3])  # range(2, 6, 2) (슬라이싱해도 range)
print(6 in r)  # True (빠르게 판별)
print(7 in r)  # False
print(r.start, r.stop, r.step)  # 0 10 2
print(list(reversed(r)))  # [8, 6, 4, 2, 0]
