"""
`@abstractmethod`는 "자식 클래스가 반드시 구현해야 하는 메서드"를 지정할 때 씁니다. `ABC`를 상속한 클래스에서만 동작합니다.
"""

from abc import ABC, abstractmethod


class Animal(ABC):
    @abstractmethod
    def speak(self) -> str:
        """자식 클래스가 반드시 구현해야 함"""

    def introduce(self) -> str:
        # 일반 메서드는 그대로 상속됨
        return f"저는 {self.speak()} 소리를 내요"


class Dog(Animal):
    def speak(self) -> str:
        return "멍멍"


class Cat(Animal):
    def speak(self) -> str:
        return "야옹"


dog = Dog()
print(dog.introduce())  # 저는 멍멍 소리를 내요
print(Cat().speak())  # 야옹
