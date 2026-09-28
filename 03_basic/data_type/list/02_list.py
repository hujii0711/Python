"""
추가
"""

fruits = ["apple", "banana"]

fruits.append("cherry")  # 맨 뒤에 추가
fruits.insert(1, "orange")  # 인덱스 1에 삽입
fruits.extend(["grape", "kiwi"])  # 여러 개 추가
print(fruits)
# ['apple', 'orange', 'banana', 'cherry', 'grape', 'kiwi']
