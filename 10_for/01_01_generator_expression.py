"""
제너레이터 표현식은 리스트 컴프리헨션과 문법이 거의 같지만, 대괄호 `[]` 대신 소괄호 `()`를 사용하여 만드는 표현식입니다.
결과를 한 번에 리스트로 만들지 않고, 값을 하나씩 필요할 때마다 생성(지연 평가, lazy evaluation)하는 제너레이터 객체를 반환합니다.

(표현식 for 변수 in 반복가능객체 if 조건)
"""

gen = (x**2 for x in range(5))
print(gen)  # <generator object <genexpr> at 0x...>
print(list(gen))  # [0, 1, 4, 9, 16]

for value in gen:
    print(value)
# 0 1 4 9 16

for value2 in (x**2 for x in range(5)):
    print(value2)
