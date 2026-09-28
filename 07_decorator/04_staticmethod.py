"""
`@staticmethod`(정적 메서드)는 `@classmethod`와 마찬가지로 인스턴스(객체)를 생성하지 않고도 클래스를 통해 바로 호출할 수 있는 메서드입니다.
가장 큰 특징은 메서드를 정의할 때 `self`나 `cls` 같은 첫 번째 인자를 받지 않는다는 점입니다.
즉, 클래스나 인스턴스의 상태(데이터)에 전혀 관여하지 않고, 독립적으로 기능을 수행하는 함수를 클래스 안에 묶어두고 싶을 때 사용합니다.
"""


class Calculator:
    @staticmethod
    def add(a, b):
        # self나 cls를 쓰지 않고, 전달받은 인자값으로만 동작합니다.
        return a + b

    @staticmethod
    def is_even(num):
        return num % 2 == 0


# 객체를 생성하지 않고 클래스 이름으로 바로 호출
result1 = Calculator.add(10, 20)
result2 = Calculator.is_even(7)

print(result1)  # 출력: 30
print(result2)  # 출력: False
