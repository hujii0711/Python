"""
여러 값 중에서 **가장 큰 값**을 반환합니다.
"""

print(max(3, 7, 2))  # 7 (여러 인자 중 최댓값)
print(max([5, 1, 9, 3]))  # 9 (리스트 안에서 최댓값)
print(max("apple", "banana"))  # 'banana' (문자열은 사전순 비교)

# 활용 예: 가장 점수가 높은 학생 찾기
점수 = {"철수": 85, "영희": 92, "민수": 78}
print(max(점수, key=점수.get))  # '영희' (key로 비교 기준 지정)

# 활용 예: 문자열 길이 기준으로 가장 긴 단어 찾기
단어들 = ["cat", "elephant", "dog"]
print(max(단어들, key=len))  # 'elephant'
