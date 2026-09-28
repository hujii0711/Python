# 비효율적
result = ""
for i in range(5):
    result += str(i)

# 권장: 반복문에서 +=로 문자열을 계속 이어붙이는 것보다 리스트에 모아서 join 한 번 하는 방식이 훨씬 효율적입니다.
result = "".join(str(i) for i in range(5))
print(result)  # 01234

# --- 자주 하는 실수
# 구분자는 마지막에 붙지 않음 (요소 사이에만 들어감)
print(",".join(["a", "b", "c"]))  # a,b,c  (끝에 , 없음)
print(type(",".join(["a", "b", "c"])))  # <class 'str'>

# 요소가 하나면 구분자가 안 보임
print(",".join(["a"]))  # a

# 빈 리스트는 빈 문자열
print(",".join([]))  # (빈 문자열)

# join은 리스트가 아니라 "구분자 문자열"의 메서드
# ["a", "b"].join(",")   -> AttributeError
