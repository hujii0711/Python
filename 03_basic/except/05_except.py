"""
예외 발생시키기 (raise)
"""


def set_age(age):
    if not isinstance(age, int):
        raise TypeError("age는 int여야 합니다")
    if age < 0:
        raise ValueError("age는 0 이상이어야 합니다")
    return age


try:
    set_age(-5)
except ValueError as e:
    print(e)  # age는 0 이상이어야 합니다
