"""
어떤 객체(변수, 모듈, 클래스 등)가 사용할 수 있는 속성과 메서드들을 리스트로 보여줍니다. "이 객체로 뭘 할 수 있지?"가 궁금할 때 유용합니다.
"""

# 문자열 객체가 가진 메서드들 확인
텍스트 = "hello"
print(dir(텍스트))
# ['__add__', ..., 'capitalize', 'count', 'find', 'lower', 'upper', ...]

# 실제로 그 메서드를 써보기
print(텍스트.upper())  # 'HELLO'

# 모듈에 어떤 함수가 있는지 확인할 때도 유용
import math

print(dir(math))
# ['acos', 'asin', 'atan', 'ceil', 'cos', 'pi', 'sqrt', ...]
