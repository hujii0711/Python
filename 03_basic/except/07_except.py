"""
예외 연결 (from)
"""

try:
    int("abc")
except ValueError as e:
    raise RuntimeError("설정값 변환 실패") from e
# 원래 예외가 원인으로 함께 표시됨
