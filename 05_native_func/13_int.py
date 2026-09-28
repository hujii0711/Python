"""
문자열이나 실수(float)를 정수(integer)로 변환합니다.
"""

print(int("10"))  # 10
print(int(3.9))  # 3 (소수점 이하는 버림, 반올림 아님!)
print(int("  7  "))  # 7 (공백은 자동으로 제거됨)

# 변환 불가능한 경우 에러 발생
print(int("hello"))  # ValueError 발생!
print(int("3.5"))  # ValueError! (소수점 있는 문자열은 바로 변환 안됨)

# 이런 경우엔 float으로 먼저 변환 후 int로
print(int(float("3.5")))  # 3

# 활용 예: input()과 함께 자주 사용
나이 = int(input("나이: "))
print(나이 * 2)
