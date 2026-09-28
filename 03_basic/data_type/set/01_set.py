"""
언제 Set을 쓰면 좋을까요?
- 데이터의 중복을 빠르게 제거해야 할 때: 리스트를 `set()`에 넣었다가 다시 `list()`로 바꾸는 테크닉은 파이썬에서 단골로 쓰입니다.
- 특정 값이 포함되어 있는지 확인할 때: 리스트에서 `if "apple" in my_list:`를 쓰면 처음부터 끝까지 다 찾아봐야 해서 속도가 느릴 수 있지만,
 세트는 내부 구조(해시 테이블) 특성상 데이터가 아무리 많아도 눈 깜짝할 사이에(`O(1)`) 찾아냅니다.
"""

s = {1, 2, 3}  # 집합
print(type(s))  # <class 'set'>
print(s)  # {1, 2, 3}
empty_set = set()  # 빈 집합 (❌ {} 아님, {}는 dict)
print(type(empty_set))  # <class 'set'>
print(empty_set)  # set()

## 주의: `{}`만 단독으로 쓰면 빈 딕셔너리가 됩니다. 빈 집합은 안 됩니다.
empty = {}
print(type(empty))  # <class 'dict'>  ❌ 집합 아님
