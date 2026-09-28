class Animal:
    name: str
    age: int

    def __init__(self, name: str, age: int) -> None:
        self.name = name
        self.age = age

    def speak(self) -> str:
        return f"{self.name} says hello"


def process_animal(animal: Animal) -> str:
    return animal.speak()
