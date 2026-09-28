"""
리스트, 튜플 등의 모든 요소가 참(True)이면 `True`, 하나라도 거짓(False)이 있으면 `False`를 반환합니다.
"""

print(all([True, True, True]))  # True
print(all([True, False, True]))  # False

# 빈 리스트는 True 취급 (주의!)
print(all([]))  # True

# 활용 예: 모든 학생이 60점 이상인지 확인
점수 = [70, 85, 60, 90]
print(all(점수 >= 60 for 점수 in 점수))  # True

점수2 = [70, 55, 60, 90]
print(all(점수 >= 60 for 점수 in 점수2))  # False (55점이 있어서)
