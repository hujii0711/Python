"""
`all()`과 반대로, 하나라도 참(True)이 있으면 `True`를 반환합니다. 모두 거짓이면 `False`.
"""

print(any([False, False, True]))  # True
print(any([False, False, False]))  # False

# 빈 리스트는 False 취급 (주의!)
print(any([]))  # False

# 활용 예: 리스트에 음수가 하나라도 있는지 확인
숫자들 = [3, 7, -2, 10]
print(any(n < 0 for n in 숫자들))  # True (-2가 있어서)
