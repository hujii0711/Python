"""
시작 번호 바꾸기 (`start` 옵션)
기본적으로 인덱스는 0부터 시작하지만, 1부터 시작하고 싶을 때가 많습니다 (예: "1번째, 2번째..." 표시).
"""

fruits = ["사과", "바나나", "체리"]

for i, fruit in enumerate(fruits, start=1):
    print(f"{i}번째: {fruit}")

"""
특정 조건의 인덱스 찾기
"""
scores = [85, 92, 78, 92, 60]

for i, score in enumerate(scores):
    if score == 92:
        print(f"{i}번 인덱스에서 92점 발견")
