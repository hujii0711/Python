# 조건 표현식(삼항 연산자)
# ② 숫자 비교
# 두 수 중 더 큰 값을 고릅니다.
a, b = 10, 20
bigger = a if a > b else b  # noqa: FURB136
print(bigger)  # 출력: 20
