"""
유용한 함수
"""

nums = [1, 2, 3, 4, 5]

print(list(map(lambda x: x * 2, nums)))  # [2, 4, 6, 8, 10]
print(list(filter(lambda x: x > 2, nums)))  # [3, 4, 5]
print(any(x > 4 for x in nums))  # True
print(all(x > 0 for x in nums))  # True

nums.reverse()  # 제자리에서 뒤집기
print(nums)  # [5, 4, 3, 2, 1]
