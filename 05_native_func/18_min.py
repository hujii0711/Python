"""
`max()`와 반대로, 여러 값 중에서 가장 작은 값을 반환합니다. 사용법은 완전히 동일해요.
"""

print(min(3, 7, 2))  # 2
print(min([5, 1, 9, 3]))  # 1
print(min("apple", "banana"))  # 'apple' (사전순으로 더 앞선 것)

# 활용 예: 가장 점수가 낮은 학생 찾기
점수 = {"철수": 85, "영희": 92, "민수": 78}
print(min(점수, key=점수.get))  # '민수'

# 활용 예: 가장 짧은 단어 찾기
단어들 = ["cat", "elephant", "dog"]
print(min(단어들, key=len))  # 'cat'
