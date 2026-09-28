"""
변수나 값이 어떤 자료형(타입)인지 알려줍니다.
"""

print(int)  # <class 'int'>
print(float)  # <class 'float'>
print(str)  # <class 'str'>
print(type([1, 2, 3]))  # <class 'list'>
print(type((1, 2)))  # <class 'tuple'>
print(type({"a": 1}))  # <class 'dict'>
print(bool)  # <class 'bool'>

# 활용 예: 디버깅할 때 변수 타입 확인
값 = input("숫자를 입력하세요: ")
print(type(값))  # <class 'str'> (input은 항상 문자열!)

# 조건문에서 타입 비교
x = 10
if type(x) == int:
    print("정수입니다.")
