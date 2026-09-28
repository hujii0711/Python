"""
예외 객체 확인 (as e)
"""

try:
    int("abc")
except ValueError as e:
    print(f"에러: {e}")  # 에러: invalid literal for int() with base 10: 'abc'
    print(type(e).__name__)  # ValueError
