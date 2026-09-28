"""
삭제
"""

items = [1, 2, 3, 4, 5, 3]

items.remove(3)  # 값으로 삭제 (첫 번째 3만)
last = items.pop()  # 마지막 요소 꺼내기 -> 3
first = items.pop(0)  # 인덱스로 꺼내기 -> 1
del items[0]  # 인덱스로 삭제
items.clear()  # 전부 삭제
