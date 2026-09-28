"""
파이썬의 `@classmethod`는 클래스 내부에서 정의되는 데코레이터로, 인스턴스(객체)가 아닌 클래스 자체를 첫 번째 인자로 받는 메서드를 만들 때 사용합니다.
쉽게 말해, 개별 데이터(인스턴스)를 다루는 게 아니라 클래스 전체와 관련된 기능이나 데이터를 다룰 때 아주 유용합니다.
대체 생성자 역할을 하는 메서드를 만들 때도 자주 사용됩니다. 예를 들어, 특정 형식의 데이터를 받아서 객체를 생성하는 등의 작업에 적합합니다.
"""


class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    # 클래스 메서드 정의
    @classmethod
    def from_birth_year(cls, name, birth_year):
        import datetime

        current_year = datetime.date.today().year
        age = current_year - birth_year
        # cls(name, age)는 결국 Person(name, age)를 호출하여 객체를 반환하는 것과 같습니다.
        return cls(name, age)

    def introduce(self):
        return f"안녕하세요, 제 이름은 {self.name}이고 {self.age}살입니다."


# 1. 일반적인 방식으로 객체 생성
p1 = Person("이몽룡", 25)
print(p1.introduce())

# 2. 클래스 메서드를 통해 태어난 연도로 객체 생성 (객체 생성 없이 바로 호출)
p2 = Person.from_birth_year("성춘향", 2000)
print(p2.introduce())
