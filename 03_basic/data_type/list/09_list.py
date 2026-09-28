"""
복사(주의)
"""

a = [1, 2, 3]
b = a  # 같은 리스트를 가리킴 (복사 아님)
b.append(4)
print(a)  # [1, 2, 3, 4]

c = a.copy()  # 얕은 복사 (a[:] 나 list(a) 도 동일)
c.append(5)
print(a)  # [1, 2, 3, 4] (영향 없음)

# 중첩 리스트는 deepcopy 필요
import copy

nested = [[1, 2], [3, 4]]
deep = copy.deepcopy(nested)
