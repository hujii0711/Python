"""
다시 던지기 (re-raise)
"""

try:
    int("abc")
except ValueError:
    print("로그 남기기")
    raise  # 같은 예외를 그대로 다시 발생시킴
