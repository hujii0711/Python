s = {1, 2, 3}

# ① 값 하나 추가하기: .add()
s.add(4)
print(s)  # {1, 2, 3, 4}

# ② 값 여러 개 추가하기: .update()
s.update([5, 6, 7])
print(s)  # {1, 2, 3, 4, 5, 6, 7}

# ③ 특정 값 삭제하기: .remove() 또는 .discard()
s.remove(3)  # 3을 삭제 (만약 3이 없으면 KeyError 에러 발생)
s.discard(99)  # 99를 삭제 (값이 없어도 에러 없이 안전하게 넘어감)
print(s)  # {1, 2, 4, 5, 6, 7}
