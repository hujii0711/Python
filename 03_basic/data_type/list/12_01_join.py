# --- 기본 사용

chars = ["p", "y", "t", "h", "o", "n"]
print("".join(chars))  # python
print("-".join(chars))  # p-y-t-h-o-n

words = ["Hello", "World"]
print("".join(words))  # HelloWorld
print(" ".join(words))  # Hello World
print(", ".join(words))  # Hello, World
print("-".join(words))  # Hello-World
print("\n".join(words))  # 줄바꿈으로 연결

# --- 다양한 구분자

date = ["2026", "09", "28"]
print("-".join(date))  # 2026-09-28
print("/".join(date))  # 2026/09/28
print(":".join(["12", "30", "45"]))  # 12:30:45

path = ["home", "user", "docs"]
print("/" + "/".join(path))  # /home/user/docs

print(" > ".join(["홈", "상품", "상세"]))  # 홈 > 상품 > 상세

# --- 문자열 뒤집기, 정렬
s = "hello"
print("".join(reversed(s)))  # olleh
print("".join(sorted(s)))  # ehllo
print("".join(sorted(s, reverse=True)))  # ollhe

# --- 컴프리헨션, 제너레이터와 함께
# 대문자만 추출
text = "Hello World Python"
print("".join(c for c in text if c.isupper()))  # HWP

# 공백 제거
print("".join(text.split()))  # HelloWorldPython

# 숫자만 추출
mixed = "a1b2c3"
print("".join(c for c in mixed if c.isdigit()))  # 123

# 모음 제거
print("".join(c for c in "banana" if c not in "aeiou"))  # bnn

# 문자 반복
print("".join("ab" for _ in range(3)))  # ababab


# --- 숫자는 str로 변환 후 사용
nums = [1, 2, 3]

# "".join(nums)
# TypeError: sequence item 0: expected str instance, int found

print("".join(str(n) for n in nums))  # 123
print(",".join(map(str, nums)))  # 1,2,3

# --- 딕셔너리, 튜플, 집합
d = {"a": 1, "b": 2, "c": 3}
print("".join(d))  # abc (키만 연결)
print(",".join(f"{k}={v}" for k, v in d.items()))  # a=1,b=2,c=3

print("-".join(("x", "y", "z")))  # x-y-z (튜플)
print("".join(sorted({"c", "a", "b"})))  # abc (집합은 순서 없으니 정렬)
