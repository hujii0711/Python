"""
리스트 등에서 특정 조건을 만족하는 요소들만 골라냅니다. 함수와 반복 가능한 객체(리스트 등)를 인자로 받아요.
`filter()`의 결과는 바로 리스트로 보이지 않고 `filter` 객체로 나오기 때문에, 눈으로 확인하려면 `list()`로 감싸줘야 합니다.
"""


def postive(x: int):
    return x > 0


a = [-1, 2, 1, 4]

print(list(filter(postive, a)))
print(list(filter(postive, [-1, 2, 1, 4])))

숫자들 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]


# 짝수만 걸러내기
def is_even(n):
    return n % 2 == 0


짝수들 = filter(is_even, 숫자들)
print(list(짝수들))  # [2, 4, 6, 8, 10]

# lambda(익명함수)와 함께 더 간결하게
짝수들2 = filter(lambda n: n % 2 == 0, 숫자들)
print(list(짝수들2))  # [2, 4, 6, 8, 10]

# 활용 예: 60점 이상인 학생 점수만 걸러내기
점수 = [55, 70, 90, 45, 60]
합격 = list(filter(lambda x: x >= 60, 점수))
print(합격)  # [70, 90, 60]
