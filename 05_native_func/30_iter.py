"""
iter() 함수는 리스트, 튜플, 문자열 같은 반복 가능한 객체(Iterable)로부터 반복자(Iterator)를 생성해 주는 내장 함수입니다.
next() 함수와 함께 사용하면 요소를 하나씩 수동으로 차례대로 꺼내올 수 있습니다.
"""

my_list = [10, 20, 30]

# 이터레이터 생성
my_iter = iter(my_list)

print(next(my_iter))  # 10
print(next(my_iter))  # 20
print(next(my_iter))  # 30
# print(next(my_iter))  # 더 이상 가져올 요소가 없으면 StopIteration 에러 발생

"""
특정 값(Sentinel)을 만날 때까지 반복하기 (iter(callable, sentinel))
iter() 함수에 함수(또는 호출 가능한 객체)와 감시자(sentinel) 값을 전달하면, 함수가 sentinel 값을 반환할 때까지 자동으로 호출을 반복하는 유용한 기능도 있습니다.
예를 들어, 특정 조건(감시자 값)이 될 때까지 입력을 받는 코드를 간결하게 작성할 수 있습니다.
"""
# input() 함수를 호출하다가 'exit'가 반환되면 반복을 멈춤
# (실행 시 'exit'를 입력하면 종료됩니다)
lines = iter(input, "exit")

for line in lines:
    print(f"입력된 값: {line}")
