"""
데코레이터는 "함수를 감싸서 추가 기능을 붙여주는 함수"예요. 원래 함수의 코드는 건드리지 않고, 그 앞뒤로 새로운 동작(로깅, 시간 측정, 권한 체크 등)을 끼워 넣을 수 있게 해줍니다.
"""


# 코드 재사용성 향상
# 같은 기능을 여러 함수에 반복 작성할 필요 없이, 데코레이터 하나로 적용할 수 있습니다.
def log(func):
    def wrapper(*args, **kwargs):
        print(args)
        print(kwargs)
        print(f"{func.__name__} 호출됨")
        return func(*args, **kwargs)

    return wrapper


@log
def add(a, b):
    return a + b


@log
def multiply(a, b):
    return a * b


print(add(1, 3))
# print(multiply(1, 3))
