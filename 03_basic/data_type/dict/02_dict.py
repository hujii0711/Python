person = {"name": "홍길동", "age": 30, "city": "서울"}

# 값 접근
print(person["name"])  # 홍길동
print(person.get("age"))  # 30
print(person.get("job", "없음"))  # 없는 키는 기본값 반환 → 없음

# 값 추가/수정
person["job"] = "개발자"
person["age"] = 31

# 값 삭제
del person["city"]

# 키 존재 확인
if "name" in person:
    print("name 키가 있습니다")

# 반복
for key, value in person.items():
    print(key, value)

for key in person:
    print(key)

for value in person.values():
    print(value)
