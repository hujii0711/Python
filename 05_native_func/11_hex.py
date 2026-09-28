"""
정수를 16진수(hexadecimal) 형태의 문자열로 바꿔줍니다.
"""

print(hex(255))  # '0xff'
print(hex(16))  # '0x10'
print(hex(10))  # '0xa'

# 앞의 '0x'는 "이건 16진수야"라는 표시
숫자 = 4096
print(hex(숫자))  # '0x1000'

# 활용 예: 색상 코드(RGB → HEX) 만들 때 자주 사용
r, g, b = 255, 0, 128
print(f"#{hex(r)[2:]}{hex(g)[2:]}{hex(b)[2:]}")  # #ff080 (자릿수 주의 필요)
