# 1. 쿼리스트링 만들기
params = {"q": "python", "page": 1}
query = "&".join(f"{k}={v}" for k, v in params.items())
print(query)  # q=python&page=1

# 2. 문장 -> 각 단어 첫 글자 대문자
sentence = "python is fun"
print(" ".join(w.capitalize() for w in sentence.split()))  # Python Is Fun

# 3. snake_case -> camelCase
name = "user_first_name"
first, *rest = name.split("_")
print(first + "".join(w.title() for w in rest))  # userFirstName

# 4. 여러 줄 텍스트 만들기
lines = ["첫째 줄", "둘째 줄", "셋째 줄"]
print("\n".join(lines))

# 5. CSV 한 줄 만들기
row = ["철수", 25, "서울"]
print(",".join(map(str, row)))  # 철수,25,서울

# 6. 리스트 사이에 구분자 넣어 출력
print("→".join(["A", "B", "C"]))  # A→B→C
