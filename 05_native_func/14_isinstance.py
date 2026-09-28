"""
어떤 객체가 특정 타입(자료형)인지 확인해서 `True`/`False`로 알려줍니다.
"""

print(isinstance(10, int))  # True
print(isinstance("hello", str))  # True
print(isinstance(3.14, int))  # False (실수는 int가 아님)

# 여러 타입 중 하나인지 한번에 확인 (튜플로 전달)
print(isinstance(10, (int, float)))  # True
print(isinstance("hi", (int, float)))  # False


# 활용 예: 함수 안에서 입력값 타입 검증
def 더하기(a, b):
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        return "숫자만 입력해주세요!"
    return a + b


print(더하기(3, 5))  # 8
print(더하기("3", 5))  # 숫자만 입력해주세요!
