# 실전 ⑦
# 딕셔너리·문자열 활용
# 다양한 자료형에서 원하는 값만 추출합니다.

# 딕셔너리 리스트에서 특정 필드 추출
users = [
    {"name": "Alice", "age": 25},
    {"name": "Bob", "age": 17},
    {"name": "Carol", "age": 30},
]

# 성인(18세 이상) 이름만
adults = [u["name"] for u in users if u["age"] >= 18]
# → ["Alice", "Carol"]

# 공백 제거 후 빈 문자열 걸러내기
raw = ["  hello  ", "", " world", "  "]
clean = [s.strip() for s in raw if s.strip()]
# → ["hello", "world"]
