# 조건 표현식(삼항 연산자)

# ⑤ 중첩 삼항 연산자 (주의!)
# 중첩은 가능하지만, 가독성이 나빠져서 남용하면 안 됩니다.

score = 75
grade = "A" if score >= 90 else "B" if score >= 80 else "C"

print(grade)  # → "C"
