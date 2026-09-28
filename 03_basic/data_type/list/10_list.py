"""
중복 제거, 합치기, 언패킹
"""

nums = [1, 2, 2, 3, 3, 3]
print(list(set(nums)))  # [1, 2, 3] (순서 보장 안 됨)
print(list(dict.fromkeys(nums)))  # [1, 2, 3] (순서 유지)

print([1, 2] + [3, 4])  # [1, 2, 3, 4]
print([0] * 3)  # [0, 0, 0]

first, *middle, last = [1, 2, 3, 4, 5]
print(first, middle, last)  # 1 [2, 3, 4] 5
