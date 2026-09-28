fruits = ["사과", "바나나", "체리"]

# 방법 1: 인덱스를 직접 관리 (번거로움)
i = 0
for fruit in fruits:
    print(i, fruit)
    i += 1

# 방법 2: range와 len 사용 (가독성 떨어짐)
for i in range(len(fruits)):
    print(i, fruits[i])

# 방법 3: enumerate 사용 (가독성 높음)
for i, fruit in enumerate(fruits):
    print(i, fruit)
