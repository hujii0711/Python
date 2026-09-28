"""
정렬
"""

data = [3, 1, 4, 1, 5, 9, 2]

data.sort()  # 원본 변경
data.sort(reverse=True)  # 내림차순
sorted_data = sorted(data)  # 원본 유지, 새 리스트 반환

words = ["banana", "kiwi", "apple"]
words.sort(key=len)  # 길이 기준 -> ['kiwi', 'apple', 'banana']

people = [("철수", 25), ("영희", 22), ("민수", 30)]
people.sort(key=lambda p: p[1])  # 나이 기준
print(people)  # [('영희', 22), ('철수', 25), ('민수', 30)]
