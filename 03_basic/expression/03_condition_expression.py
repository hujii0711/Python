# 조건 표현식(삼항 연산자)

# ③ 함수 안에서 바로 반환
# 함수의 return 문에서 직접 사용할 수 있습니다.
def is_even(n):
    return "짝수" if n % 2 == 0 else "홀수"


print(is_even(4))  # → 짝수
print(is_even(7))  # → 홀수
