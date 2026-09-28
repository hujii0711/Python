"""
enumerate는 정확히 무엇을 하나?
`enumerate(리스트)`는 각 요소를 (인덱스, 값) 형태의 짝(튜플)으로 만들어줍니다.
"""

fruits = ["사과", "바나나", "체리"]
result = list(enumerate(fruits))
print(result)  # [(0, '사과'), (1, '바나나'), (2, '체리')]
# 이렇게 `(0, '사과')`, `(1, '바나나')`, `(2, '체리')` 처럼 인덱스와 값을 짝지어주는 것이 enumerate의 핵심 역할입니다.

for i, fruit in enumerate(fruits):
    #  ↑     ↑
    # 인덱스  값
    print(i, fruit)

fruits2 = ["사과", "바나나", "체리"]

for fruit in enumerate(fruits2):
    print(fruit)
