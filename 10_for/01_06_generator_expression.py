# 특징 4: 함수 인자로 바로 사용할 때 괄호 생략 가능
# 제너레이터 표현식이 함수의 유일한 인자로 쓰일 경우, 소괄호를 한 번만 써도 됩니다.
# 괄호 생략 가능 (함수 호출 괄호와 겸용)
total = sum(x**2 for x in range(5))
print(total)  # 30

# 다른 인자가 있으면 반드시 괄호로 감싸야 함
result = sorted((x for x in [3, 1, 2]), reverse=True)
