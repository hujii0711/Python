# 조건 표현식(삼항 연산자)
# ① 가장 기본 형태
age = 20
if age >= 18:
    result = "성인"
else:
    result = "미성년자"
# ↓ 한 줄로 줄이면
result = "성인" if age >= 18 else "미성년자"
print(result)  # 출력: 성인
