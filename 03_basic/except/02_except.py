"""
여러 예외 처리
"""


def parse_age(value):
    try:
        age = int(value)
        return 100 / age
    except ValueError:
        print("숫자가 아닙니다")
    except ZeroDivisionError:
        print("0은 사용할 수 없습니다")


parse_age("abc")  # 숫자가 아닙니다
parse_age("0")  # 0은 사용할 수 없습니다

# 여러 예외를 한 번에 묶기
try:
    int("abc")
except (ValueError, TypeError):
    print("변환 실패")
