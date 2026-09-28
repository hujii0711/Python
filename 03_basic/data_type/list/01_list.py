"""
생성과 접근
"""

nums = [10, 20, 30, 40, 50]
mixed = [1, "hello", 3.14, True, [1, 2]]  # 타입이 섞여도 됨
empty = []

print(nums[0])  # 10
print(nums[-1])  # 50 (마지막)
print(nums[1:3])  # [20, 30]
print(nums[::2])  # [10, 30, 50] (2칸씩)
print(nums[::-1])  # [50, 40, 30, 20, 10] (뒤집기)
