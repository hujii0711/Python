"""
`Greeter` 클래스 내부에 `__call__` 메서드가 정의되어 있기 때문에, `greeter`는 단순한 데이터 변수가 아니라 "호출 가능한 객체(Callable Object)"가 됩니다.
Hugging Face의 `pipe` 역시 이와 같은 원리로 설계되어 있어서, 복잡한 내부 로직을 함수를 쓰듯 `pipe(prompt)` 형태로 간단하게 실행할 수 있는 것입니다.
"""


class Greeter:
    def __init__(self, greeting_word):
        self.greeting_word = greeting_word

    def __call__(self, name):
        # 변수 뒤에 괄호()를 붙여 호출할 때 내부적으로 이 메서드가 실행됩니다.
        return f"{self.greeting_word}, {name}님!"


# 1. 객체를 생성하여 변수에 할당합니다 (Hugging Face의 pipeline()과 유사)
greeter = Greeter("안녕하세요")

# 2. 함수처럼 변수를 바로 호출합니다 (pipe(prompt)와 유사)
result = greeter("홍길동")
print(result)
# 출력: 안녕하세요, 홍길동님!
