# 기초 ②
# 문자열 리스트 변환
# 문자열 메서드도 그대로 사용할 수 있습니다.
words = ["apple", "banana", "cherry"]

# 모두 대문자로
upper = [w.upper() for w in words]
# → ["APPLE", "BANANA", "CHERRY"]

# 글자 수 구하기
lengths = [len(w) for w in words]
# → [5, 6, 6]
